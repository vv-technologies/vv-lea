@echo off
cd /d "C:\VV_GITHUB\vv-lea"
git add online/index.html
git status
git commit -m "LEA Premium UX: toast notifications, CP modal, AI badge, loading states"
git push origin main
echo DONE
