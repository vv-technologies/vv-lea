# LEA Local — Backend Python

Serverul local care rulează pe laptopul tău. Nicio conexiune externă necesară.

## Pornire

```batch
launchers\LEA_START.bat
```

## Oprire

```batch
launchers\STOP_LEA.bat
```

## Endpoint-uri

| Method | Path | Descriere |
|--------|------|-----------|
| GET | / | Workspace UI |
| GET | /status | Status server |
| GET | /generate_code | Generează cod pairing |
| POST | /pair | Conectare cu cod |
| POST | /execute | Execută comandă |
| POST | /approve | Aprobă acțiune pending |
| POST | /ask | Întreabă TinyLlama |
| GET | /ask_status | Status model AI |

## Setup complet → vezi `../docs/SETUP.md`
