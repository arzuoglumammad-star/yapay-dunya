# Yapay Dünya App Terminal

Yapay Dünya uygulamasından Codespace Linux ortamına bağlanan mobil terminal.

## API

- GET `/api/status`
- GET `/api/system`
- POST `/api/command`

## Port

8791

## Ana sistem

- World API: 8790
- App Terminal: 8791
- Project: `/workspaces/yapay-dunya`

## Güvenlik

Tehlikeli sistem komutlarının bir bölümü engellenir.
Komutlar 30 saniye timeout ile çalışır.

Bu terminali internete açık ve kimlik doğrulamasız bir üretim sunucusu olarak kullanmayın.
