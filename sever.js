// server.js
// Требования: Node.js, установить пакеты: npm install express axios body-parser
// Запуск: node server.js
// Этот сервер обрабатывает API запросы и проксирует их к Garena Open API.

const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public'))); // отдаем HTML

// Вспомогательная функция для логирования на сервере
function serverLog(message) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${message}`);
}

// Маршрут: Проверка здоровья сервера
app.get('/api/health', (req, res) => {
    serverLog('Запрос здоровья от клиента');
    res.json({
        status: 'ok',
        service: 'FF Garena Account Checker',
        timestamp: new Date().toISOString(),
        endpoints: {
            check: 'POST /api/check',
            docs: 'В теле: { "player_id": "...", "access_token": "..." }'
        }
    });
});

// Маршрут: Основная проверка аккаунта через Garena API
app.post('/api/check', async (req, res) => {
    const { player_id, access_token } = req.body;

    // Логирование входящих данных (скрываем часть токена)
    const maskedToken = access_token ? access_token.substring(0, 6) + '...' : 'отсутствует';
    serverLog(`ЗАПРОС НА ПРОВЕРКУ: ID=${player_id}, Token=${maskedToken}`);

    // Валидация входных данных
    if (!player_id || !access_token) {
        serverLog('Ошибка: не указан player_id или access_token');
        return res.status(400).json({
            status: 'error',
            code: 400,
            message: 'Требуются поля: player_id и access_token',
            example: { player_id: '123456789', access_token: 'ваш_токен_от_api' }
        });
    }

    // Конфигурация запроса к Garena Open API
    // ВАЖНО: Замените 'YOUR_GARENA_API_KEY' на реальный ключ, полученный от Garena Developer Portal.
    const GARENA_API_KEY = 'YOUR_GARENA_API_KEY'; // <-- ВСТАВЬТЕ РЕАЛЬНЫЙ API КЛЮЧ ЗДЕСЬ
    const GARENA_BASE_URL = 'https://api.garena.com'; // Официальный базовый URL

    try {
        serverLog(`Отправка запроса в Garena API: ${GARENA_BASE_URL}/rest/v1/user/info?uid=${player_id}`);
        
        // Реальный эндпоинт Garena для получения информации о пользователе
        const garenaResponse = await axios.get(`${GARENA_BASE_URL}/rest/v1/user/info`, {
            params: {
                uid: player_id,
                region: 'ID' // Регион Индонезии, можно сменить на TH, TW, VN и т.д.
            },
            headers: {
                'Authorization': `Bearer ${access_token}`, // Используем токен клиента
                'x-api-key': GARENA_API_KEY,
                'Accept': 'application/json',
                'User-Agent': 'FF-Checker-Tool/1.0'
            },
            timeout: 10000 // 10 секунд таймаут
        });

        // Обработка успешного ответа
        const userData = garenaResponse.data;
        serverLog(`Успех: Получены данные для UID ${player_id}. Ник: ${userData.nickname || 'N/A'}`);

        // Формируем структурированный ответ для клиента
        res.json({
            status: 'success',
            checked_at: new Date().toISOString(),
            account_info: {
                uid: userData.uid || player_id,
                nickname: userData.nickname || 'Неизвестно',
                level: userData.level || 0,
                region: userData.region || 'ID',
                avatar_url: userData.avatar || '',
                is_verified: userData.verified || false,
                last_login: userData.last_login || null
            },
            raw_api_response: userData // полный ответ для отладки
        });

    } catch (error) {
        // Детальная обработка ошибок
        serverLog(`ОШИБКА GARENA API: ${error.message}`);
        
        let errorResponse = {
            status: 'error',
            code: 502,
            message: 'Ошибка при обращении к Garena API',
            details: error.message
        };

        if (error.response) {
            // Сервер Garena ответил с ошибкой
            errorResponse.code = error.response.status;
            errorResponse.garena_error = error.response.data;
            
            switch(error.response.status) {
                case 401:
                    errorResponse.message = 'Неверный или просроченный Access Token.';
                    break;
                case 403:
                    errorResponse.message = 'Доступ запрещен. Проверьте API ключ и права токена.';
                    break;
                case 404:
                    errorResponse.message = 'Игрок с таким ID не найден.';
                    break;
                case 429:
                    errorResponse.message = 'Слишком много запросов. Попробуйте позже.';
                    break;
                default:
                    errorResponse.message = `Ошибка Garena: ${error.response.status}`;
            }
            serverLog(`Детали ошибки: ${JSON.stringify(error.response.data)}`);
        } else if (error.request) {
            errorResponse.message = 'Нет ответа от серверов Garena. Проверьте подключение.';
            errorResponse.code = 504;
        }

        res.status(errorResponse.code >= 500 ? 502 : errorResponse.code).json(errorResponse);
    }
});

// Запуск сервера
app.listen(PORT, () => {
    console.log(`
    ╔══════════════════════════════════════════╗
    ║   FF GARENA ACCOUNT CHECKER API        ║
    ║   Сервер запущен на порту: ${PORT}        ║
    ║   Откройте http://localhost:${PORT}      ║
    ╚══════════════════════════════════════════╝
    `);
    console.log('Для остановки нажмите Ctrl+C');
});
