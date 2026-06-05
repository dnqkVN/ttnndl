// server.js
// Требования: Node.js, установить пакеты: npm install express axios body-parser
// Запуск: node server.js
// Теперь сервер автоматически получает токен по ID, используя внутренний API ключ.

const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// Вспомогательная функция для логирования на сервере
function serverLog(message) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${message}`);
}

// ------------------------------------------------------------
// КОНФИГУРАЦИЯ: СЮДА ВСТАВЬТЕ ВАШ ГЛАВНЫЙ API КЛЮЧ GARENA
// Этот ключ будет использоваться для получения временного токена по ID.
// ------------------------------------------------------------
const MASTER_API_KEY = 'YOUR_GARENA_MASTER_API_KEY'; // <-- ОБЯЗАТЕЛЬНО ВСТАВИТЬ РЕАЛЬНЫЙ КЛЮЧ
const GARENA_BASE_URL = 'https://api.garena.com';

// Функция получения токена по ID игрока
async function fetchTokenByPlayerId(playerId) {
    serverLog(`Попытка получить токен для Player ID: ${playerId}`);
    
    try {
        // Эндпоинт для аутентификации/получения токена по UID
        // Этот запрос использует мастер-ключ сервера для генерации гостевого токена
        const tokenResponse = await axios.post(
            `${GARENA_BASE_URL}/rest/v1/auth/guest_token`,
            {
                uid: playerId,
                platform: 'android', // или 'ios'
                region: 'ID'
            },
            {
                headers: {
                    'x-api-key': MASTER_API_KEY,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout: 10000
            }
        );

        if (tokenResponse.data && tokenResponse.data.access_token) {
            const newToken = tokenResponse.data.access_token;
            serverLog(`Токен успешно получен для ID ${playerId}: ${newToken.substring(0, 8)}...`);
            return newToken;
        } else {
            throw new Error('Токен не найден в ответе Garena API');
        }
    } catch (error) {
        serverLog(`Ошибка получения токена: ${error.message}`);
        throw error;
    }
}

// Маршрут: Проверка здоровья сервера
app.get('/api/health', (req, res) => {
    serverLog('Запрос здоровья от клиента');
    res.json({
        status: 'ok',
        service: 'FF Garena Account Checker (Авто-токен)',
        timestamp: new Date().toISOString(),
        endpoints: {
            check: 'POST /api/check',
            docs: 'Теперь достаточно отправить только { "player_id": "..." }. Токен будет получен автоматически.'
        }
    });
});

// Маршрут: Основная проверка аккаунта. Требуется ТОЛЬКО player_id.
app.post('/api/check', async (req, res) => {
    const { player_id } = req.body;

    serverLog(`ЗАПРОС НА ПРОВЕРКУ: ID=${player_id}`);

    // Валидация входных данных
    if (!player_id) {
        serverLog('Ошибка: не указан player_id');
        return res.status(400).json({
            status: 'error',
            code: 400,
            message: 'Требуется поле: player_id',
            example: { player_id: '123456789' }
        });
    }

    try {
        // Шаг 1: Получаем свежий токен для этого ID, используя мастер-ключ
        serverLog('Шаг 1: Получение access_token...');
        const access_token = await fetchTokenByPlayerId(player_id);

        // Шаг 2: Используем полученный токен для запроса информации об аккаунте
        serverLog('Шаг 2: Запрос информации об аккаунте...');
        const garenaResponse = await axios.get(`${GARENA_BASE_URL}/rest/v1/user/info`, {
            params: {
                uid: player_id,
                region: 'ID'
            },
            headers: {
                'Authorization': `Bearer ${access_token}`,
                'x-api-key': MASTER_API_KEY,
                'Accept': 'application/json',
                'User-Agent': 'FF-AutoChecker/1.0'
            },
            timeout: 10000
        });

        // Обработка успешного ответа
        const userData = garenaResponse.data;
        serverLog(`Успех: Получены данные. Ник: ${userData.nickname || 'N/A'}, Уровень: ${userData.level || 0}`);

        // Формируем ответ
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
                last_login: userData.last_login || null,
                auto_token_used: access_token.substring(0, 10) + '...' // Частично показываем токен для отладки
            },
            raw_api_response: userData
        });

    } catch (error) {
        serverLog(`ОШИБКА: ${error.message}`);
        
        let errorResponse = {
            status: 'error',
            code: 502,
            message: 'Не удалось проверить аккаунт',
            details: error.message
        };

        if (error.response) {
            errorResponse.code = error.response.status;
            errorResponse.garena_error = error.response.data;
            
            switch(error.response.status) {
                case 401:
                    errorResponse.message = 'Мастер-ключ недействителен. Проверьте MASTER_API_KEY.';
                    break;
                case 403:
                    errorResponse.message = 'Доступ запрещен. Возможно, ID заблокирован или регион не совпадает.';
                    break;
                case 404:
                    errorResponse.message = 'Игрок с таким ID не найден.';
                    break;
                default:
                    errorResponse.message = `Ошибка Garena: ${error.response.status}`;
            }
        } else if (error.request) {
            errorResponse.message = 'Сервера Garena недоступны.';
            errorResponse.code = 504;
        }

        res.status(errorResponse.code >= 500 ? 502 : errorResponse.code).json(errorResponse);
    }
});

// Запуск сервера
app.listen(PORT, () => {
    console.log(`
    ╔══════════════════════════════════════════╗
    ║   FF GARENA ACCOUNT CHECKER           ║
    ║   (РЕЖИМ: АВТО-ТОКЕН ПО ID)          ║
    ║   Сервер запущен на порту: ${PORT}        ║
    ║   Откройте http://localhost:${PORT}      ║
    ╚══════════════════════════════════════════╝
    `);
});
