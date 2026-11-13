<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg">
  <img src="assets/header-light.svg" width="760" alt="curl -sI github.com/roma2246 → HTTP/2 500, потом 200. Ramazan Gabdulgumarov, fullstack, typescript, python, go">
</picture>

Делаю фуллстек: фронт на React, бэк на Node, FastAPI или Go. Иногда с ML.

### Сейчас

**holdfast** `Go`
Линтер инструкций и предохранитель для ИИ-агентов (Claude Code, Cursor, Codex). Встаёт в Claude Code как PreToolUse-хук: необратимое вроде `rm -rf ~`, `git push --force` или `curl | sh` запрещает и подсказывает, как правильно; обратимое пропускает и делает снапшот. Правила из `CLAUDE.md` превращает в проверяемые. Один статический бинарник, хук отвечает примерно за 50 мкс. Репозиторий пока закрыт.

### Проекты

- **Qairu**: платформа клуба настольного тенниса. Аккаунты, роли, мероприятия, запись с лимитами, рейтинг Elo. `React 19` `TypeScript` `Node` `Neon`
- **[EmoCam](https://github.com/roma2246/FACE_Detect)**: эмоции по веб-камере прямо в браузере. Модель обучена на PyTorch и экспортирована в ONNX, лицо ищет MediaPipe. `PyTorch` `ONNX` `onnxruntime-web` `React`
- **ARTSPACE**: сайт арт-клуба с 3D на three.js и загрузкой работ в S3. Промо-ролик к нему со звуком, который синтезирован с нуля на numpy. `React` `three.js` `Express` `Postgres`
- **QAIRU karta**: 3D-карта учебного корпуса по векторным планам этажей. `react-three-fiber` `zustand`
- **LOOKI**: персональный стилист. Гардероб, чат, удаление фона и модели прямо в браузере. `React 19` `transformers.js` `Express`

<details>
<summary>ещё</summary>
<br>

- **IELTS Helper**: подготовка к IELTS с Gemini. `React` `Express` `SQLite`
- **[Vibe_wear](https://github.com/roma2246/Vibe_wear)**: фронт магазина одежды. `React` `Tailwind` `framer-motion`
- **[StudyMate](https://github.com/roma2246/StudyMate)** + [бэк на Java](https://github.com/roma2246/StudyMate_back)
- **[map_front](https://github.com/roma2246/map_front)** + [map_back](https://github.com/roma2246/map_back): карта на Flutter
- **Go**: piscine в tomorrow school, REST API на chi + pgx

</details>

### Стек

```
языки    TypeScript, JavaScript, Python, Go, SQL; немного Dart и Java
фронт    React, Vite, Tailwind, three.js / react-three-fiber, framer-motion, MUI
бэк      Node + Express, FastAPI, Go (chi, pgx), PostgreSQL / Neon, Supabase, SQLite
ml       PyTorch, Triton, ONNX, MediaPipe, transformers.js
llm      Claude, Gemini, Vertex AI
прочее   Docker, GitHub Actions
```

### Статус

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/status-dark.svg">
  <img src="assets/status-light.svg" width="100%" alt="Активность по коммитам за последние 45 дней">
</picture>

<sub>Настоящие коммиты за 45 дней, без названий репозиториев и сообщений. Обновляет <a href="scripts/status.py">скрипт</a> раз в сутки.</sub>
