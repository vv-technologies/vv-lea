from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import time
import os
import mimetypes

# C:\LEA_CORE (doua nivele sus fata de core/servers/)
import sys

LEA_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INTERFACE_DIR = os.path.join(LEA_ROOT, 'interface')

if LEA_ROOT not in sys.path:
    sys.path.insert(0, LEA_ROOT)

API_ROUTES_GET = {'/generate_code', '/status', '/pending_actions'}
API_ROUTES_POST = {'/pair', '/set_mode', '/execute', '/approve'}

JOURNAL_PATH = os.path.join(LEA_ROOT, 'data', 'logs', 'development_journal.md')

def _journal(entry_type, detail, success=True):
    icon = '✅' if success else '❌'
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    short = str(detail)[:60].replace('|', '/')
    line = f'| {ts} | {entry_type} | {short} | {icon} |\n'
    try:
        with open(JOURNAL_PATH, 'a', encoding='utf-8') as f:
            f.write(line)
    except Exception:
        pass

class PairingServer(BaseHTTPRequestHandler):

    pairing_code = None
    paired_session = None
    pending_actions = []
    action_mode = 'manual'

    def log_message(self, format, *args):
        pass  # suprima logurile HTTP default, prea verbose

    def _serve_static(self):
        path = self.path.split('?')[0]

        if path == '/':
            file_path = os.path.join(INTERFACE_DIR, 'workspace', 'index.html')
        else:
            clean = os.path.normpath(path.lstrip('/\\'))
            file_path = os.path.join(INTERFACE_DIR, clean)

        # Protectie directory traversal
        if not os.path.abspath(file_path).startswith(os.path.abspath(INTERFACE_DIR)):
            self._send_json({'error': 'Forbidden'}, 403)
            return

        if not os.path.isfile(file_path):
            self._send_json({'error': 'Not found', 'path': path}, 404)
            return

        mime, _ = mimetypes.guess_type(file_path)
        mime = mime or 'application/octet-stream'

        with open(file_path, 'rb') as f:
            content = f.read()

        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_GET(self):
        try:
            api_path = self.path.split('?')[0]

            if api_path == '/generate_code':
                PairingServer.pairing_code = str(random.randint(100000, 999999))
                PairingServer.paired_session = None
                self._send_json({
                    'code': PairingServer.pairing_code,
                    'expires': time.time() + 300
                })
                print(f"[PAIRING CODE] {PairingServer.pairing_code}")

            elif api_path == '/status':
                try:
                    from core.ai.lea_llm import get_status as _ai_status
                    ai_st = _ai_status()
                except Exception:
                    ai_st = 'not_loaded'
                self._send_json({
                    'paired': PairingServer.paired_session is not None,
                    'mode': PairingServer.action_mode,
                    'pending_actions': len(PairingServer.pending_actions),
                    'ask_status': ai_st
                })

            elif api_path == '/pending_actions':
                self._send_json({'actions': PairingServer.pending_actions})

            elif api_path == '/ask_status':
                try:
                    from core.ai.lea_llm import get_status
                    st = get_status()
                    self._send_json({'status': st, 'ask_status': st})
                except ImportError:
                    self._send_json({'status': 'not_installed', 'ask_status': 'not_installed'})

            else:
                # Serveste fisiere statice din interface/
                self._serve_static()

        except Exception as e:
            self._send_json({'success': False, 'error': str(e)}, 500)

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            data = json.loads(post_data.decode('utf-8'))
        except Exception as e:
            self._send_json({'success': False, 'error': f'Bad request: {e}'}, 400)
            return

        try:
            if self.path == '/pair':
                code = data.get('code')
                if code == PairingServer.pairing_code:
                    PairingServer.paired_session = {
                        'session_id': str(random.randint(10000, 99999)),
                        'timestamp': time.time()
                    }
                    self._send_json({
                        'success': True,
                        'session_id': PairingServer.paired_session['session_id'],
                        'message': 'Pairing successful!'
                    })
                    print(f"[PAIRED] Session: {PairingServer.paired_session['session_id']}")
                else:
                    self._send_json({'success': False, 'error': 'Invalid pairing code'})

            elif self.path == '/set_mode':
                PairingServer.action_mode = data.get('mode', 'manual')
                self._send_json({'success': True, 'mode': PairingServer.action_mode})
                print(f"[MODE] Changed to: {PairingServer.action_mode}")

            elif self.path == '/execute':
                # FIX: verifica daca e paired inainte de .get()
                if PairingServer.paired_session is None:
                    self._send_json({'success': False, 'error': 'Not paired'})
                    return

                session_id = data.get('session_id')
                if session_id != PairingServer.paired_session.get('session_id'):
                    self._send_json({'success': False, 'error': 'Invalid session'})
                    return

                command = data.get('command')
                if not command:
                    self._send_json({'success': False, 'error': 'No command provided'})
                    return

                if PairingServer.action_mode == 'manual':
                    PairingServer.pending_actions.append({
                        'id': len(PairingServer.pending_actions),
                        'command': command,
                        'timestamp': time.time()
                    })
                    self._send_json({
                        'success': True,
                        'pending': True,
                        'message': 'Waiting for approval'
                    })
                    print(f"[PENDING] Action needs approval: {command.get('type')}")
                else:
                    result = self.execute_command(command)
                    self._send_json(result)
                    print(f"[AUTO EXECUTE] {command.get('type')}")
                    _journal('AUTO_EXEC', f"{command.get('type')} {command.get('path','')}", result.get('success', False))

            elif self.path == '/approve':
                action_id = data.get('action_id')
                if action_id is None or action_id >= len(PairingServer.pending_actions):
                    self._send_json({'success': False, 'error': 'Invalid action ID'})
                    return

                action = PairingServer.pending_actions[action_id]
                result = self.execute_command(action['command'])
                PairingServer.pending_actions.pop(action_id)
                self._send_json(result)
                print(f"[APPROVED] Action {action_id} executed")
                _journal('APPROVED', f"{action['command'].get('type')} {action['command'].get('path','')}", result.get('success', False))

            elif self.path == '/ask':
                question = data.get('question', '').strip()
                extra_ctx = data.get('context', '')
                if not question:
                    self._send_json({'success': False, 'error': 'No question'})
                    return
                try:
                    from core.ai.lea_llm import ask
                    answer, status, source = ask(question, extra_ctx)
                    if status == 'ok':
                        self._send_json({'success': True, 'answer': answer, 'source': source})
                        _journal('ASK_LEA', f'[{source}] {question[:55]}', True)
                    else:
                        self._send_json({'success': False, 'error': status,
                                        'message': 'Eroare la procesarea întrebării.'})
                except Exception as e:
                    self._send_json({'success': False, 'error': 'orchestrator_error',
                                    'message': str(e)})

            else:
                self._send_json({'error': 'Not found'}, 404)

        except Exception as e:
            self._send_json({'success': False, 'error': str(e)}, 500)

    def execute_command(self, command):
        try:
            cmd_type = command.get('type')

            if cmd_type == 'CREATE_FILE':
                path = command.get('path', '')
                content = command.get('content', '')
                dir_path = os.path.dirname(path)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {'success': True, 'message': f'File created: {path}'}

            elif cmd_type == 'READ_FILE':
                path = command.get('path', '')
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {'success': True, 'content': content}

            elif cmd_type == 'LIST_DIR':
                path = command.get('path', 'C:\\LEA_CORE\\data')
                items = os.listdir(path)
                return {'success': True, 'items': items}

            else:
                return {'success': False, 'error': f'Unknown command type: {cmd_type}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}


def run_pairing_server(port=9999):
    server_address = ('', port)
    httpd = HTTPServer(server_address, PairingServer)

    print("=" * 60)
    print("  LEA PAIRING SERVER - Ready for Connection")
    print("=" * 60)
    print(f"  Server: http://localhost:{port}")
    print(f"  Token:  LEA-TRINITY-2026-PRO")
    print(f"  Mode:   MANUAL (default)")
    print("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] LEA Server stopped")


if __name__ == '__main__':
    run_pairing_server()
