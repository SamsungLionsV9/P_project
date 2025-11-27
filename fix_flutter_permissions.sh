#!/bin/bash
echo "Flutter 권한 문제 해결 스크립트"
echo "비밀번호를 입력하세요:"
sudo chown -R $(whoami) ~/.config
mkdir -p ~/.config/flutter
echo "✅ 권한 문제 해결 완료!"
