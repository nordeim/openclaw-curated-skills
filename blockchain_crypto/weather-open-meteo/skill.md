---
name: weather-open-meteo
description: "Obter condições climáticas atuais e previsões via open-meteo.com, usando apenas curl. Caso falhe, recorre ao wttr.in."
homepage: https://open-meteo.com/
metadata: {
  "openclaw": {
    "emoji": "🌤️"
  }
}
cmd: api
---
# Weather Open‑Meteo (cURL único)

Free weather service – solicita via cURL à API do Open‑Meteo e devolve JSON. Se qualquer etapa falhar, usa **wttr.in** como fallback.

> **Requisitos**
> - Bash/SH (GNU)
> - `curl` disponível
> - `grep` e `sed` padrão

## Exemplo de uso

```bash
./bin/weather-open-meteo "São Paulo"
```

Output (JSON de Open‑Meteo ou texto de wttr.in).