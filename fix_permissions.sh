#!/bin/bash
echo "권한 수정 중..."
sudo chown -R $(whoami) ~/.config
mkdir -p ~/.config/flutter
echo "✅ 권한 수정 완료!"
