# Yapay Dünya Linux

Bu uygulama Yapay Dünya PWA içinden Remote Linux Center'a bağlanır.

## Mimari

Telefon
↓
Yapay Dünya uygulaması
↓
Linux Terminal UI
↓
Linux Center API :8787
↓
GitHub Codespace Linux

## API

GET /api/status
GET /api/system
POST /api/terminal

## Güvenlik

Terminal API kontrollü komut çalıştırma katmanıdır.
Portu herkese açık internete açmayın.
