const API_BASE_URL = 'http://localhost:5000/api/auth';
const USER_API_BASE_URL = 'http://localhost:5000/api/users';

class AuthAPI {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    getTokens() {
        return {
            accessToken: localStorage.getItem('access_token'),
            refreshToken: localStorage.getItem('refresh_token')
        };
    }

    setTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        if (refreshToken) {
            localStorage.setItem('refresh_token', refreshToken);
        }
    }

    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    getHeaders(includeAuth = false) {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (includeAuth) {
            const tokens = this.getTokens();
            if (tokens.accessToken) {
                headers['Authorization'] = `Bearer ${tokens.accessToken}`;
            }
        }
        
        return headers;
    }

    async request(endpoint, method = 'GET', data = null, includeAuth = false, retryOn401 = true) {
        try {
            const options = {
                method: method,
                headers: this.getHeaders(includeAuth)
            };

            if (data && (method === 'POST' || method === 'PUT')) {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(`${this.baseURL}${endpoint}`, options);
            const result = await response.json();

            // Nếu nhận được 401 và có includeAuth và retryOn401, thử refresh token
            if (response.status === 401 && includeAuth && retryOn401 && endpoint !== '/refresh') {
                const tokens = this.getTokens();
                if (tokens.refreshToken) {
                    const refreshResult = await this.refreshToken();
                    if (refreshResult.success) {
                        // Retry request với token mới (chỉ retry 1 lần)
                        return await this.request(endpoint, method, data, includeAuth, false);
                    } else {
                        // Refresh thất bại, xóa tokens
                        this.clearTokens();
                        return {
                            success: false,
                            data: null,
                            message: 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.',
                            errors: null,
                            status: 401
                        };
                    }
                } else {
                    // Không có refresh token, xóa tokens
                    this.clearTokens();
                    return {
                        success: false,
                        data: null,
                        message: 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.',
                        errors: null,
                        status: 401
                    };
                }
            }

            return {
                success: result.success,
                data: result.data,
                message: result.message,
                errors: result.errors,
                status: response.status
            };
        } catch (error) {
            return {
                success: false,
                message: 'Lỗi kết nối đến server. Vui lòng thử lại sau.',
                error: error.message,
                status: 0
            };
        }
    }

    async register(email, password, fullName, phone = null) {
        const result = await this.request('/register', 'POST', {
            email,
            password,
            full_name: fullName,
            phone
        });

        if (result.success && result.data) {
            this.setTokens(result.data.access_token, result.data.refresh_token);
        }

        return result;
    }

    async login(email, password) {
        const result = await this.request('/login', 'POST', {
            email,
            password
        });

        if (result.success && result.data) {
            this.setTokens(result.data.access_token, result.data.refresh_token);
        }

        return result;
    }

    async logout() {
        const tokens = this.getTokens();
        
        if (!tokens.accessToken) {
            this.clearTokens();
            return { success: false, message: 'Bạn chưa đăng nhập' };
        }

        try {
            const result = await this.request('/logout', 'POST', null, true);
            this.clearTokens();
            return result;
        } catch (error) {
            this.clearTokens();
            return {
                success: false,
                message: 'Lỗi khi đăng xuất',
                error: error.message
            };
        }
    }

    async refreshToken() {
        const tokens = this.getTokens();
        if (!tokens.refreshToken) {
            return { success: false, message: 'Không có refresh token' };
        }

        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${tokens.refreshToken}`
        };

        try {
            const response = await fetch(`${this.baseURL}/refresh`, {
                method: 'POST',
                headers: headers
            });
            const result = await response.json();

            if (result.success && result.data) {
                this.setTokens(result.data.access_token, tokens.refreshToken);
            }

            return {
                success: result.success,
                data: result.data,
                message: result.message,
                status: response.status
            };
        } catch (error) {
            return {
                success: false,
                message: 'Lỗi làm mới token',
                error: error.message
            };
        }
    }

    async forgotPassword(email) {
        return await this.request('/forgot-password', 'POST', { email });
    }

    async resetPassword(token, newPassword) {
        return await this.request('/reset-password', 'POST', {
            token,
            new_password: newPassword
        });
    }

    async verifyEmail(token) {
        return await this.request('/verify-email', 'POST', { token });
    }

    async resendVerification() {
        return await this.request('/resend-verification', 'POST', null, true);
    }

    async verifyToken() {
        return await this.request('/verify-token', 'GET', null, true);
    }
}

const authAPI = new AuthAPI();

function isLoggedIn() {
    const tokens = authAPI.getTokens();
    return !!tokens.accessToken;
}

async function verifyTokenWithBackend() {
    const tokens = authAPI.getTokens();
    if (!tokens.accessToken) {
        return false;
    }

    try {
        const result = await authAPI.verifyToken();
        if (result.success) {
            return true;
        }
        
        // Nếu token không hợp lệ, thử refresh token
        if (result.status === 401 && tokens.refreshToken) {
            const refreshResult = await authAPI.refreshToken();
            if (refreshResult.success) {
                // Thử verify lại với token mới
                const verifyResult = await authAPI.verifyToken();
                return verifyResult.success;
            }
        }
        
        return false;
    } catch (error) {
        // Nếu có lỗi, thử refresh token trước khi xóa
        if (tokens.refreshToken) {
            try {
                const refreshResult = await authAPI.refreshToken();
                if (refreshResult.success) {
                    const verifyResult = await authAPI.verifyToken();
                    return verifyResult.success;
                }
            } catch (refreshError) {
                // Nếu refresh cũng thất bại, xóa tokens
                authAPI.clearTokens();
            }
        } else {
            authAPI.clearTokens();
        }
        return false;
    }
}

async function redirectIfLoggedIn(redirectUrl = '../index.html') {
    const isValid = await verifyTokenWithBackend();
    if (isValid) {
        window.location.href = redirectUrl;
    } else {
        authAPI.clearTokens();
    }
}

function redirectIfNotLoggedIn(redirectUrl = 'auth/login.html') {
    if (!isLoggedIn()) {
        window.location.href = redirectUrl;
    }
}

async function logout() {
    const result = await authAPI.logout();
    
    if (result.success) {
        showMessage(result.message || 'Đăng xuất thành công!', 'success');
    } else {
        showMessage('Đã đăng xuất', 'success');
    }
    
    setTimeout(() => {
        window.location.href = 'auth/login.html';
    }, 1000);
}

function showMessage(message, type = 'success') {
    const existingMessages = document.querySelectorAll('.message-alert');
    existingMessages.forEach(msg => msg.remove());

    const messageDiv = document.createElement('div');
    messageDiv.className = `message-alert ${type}`;
    messageDiv.textContent = message;
    
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        max-width: 400px;
    `;

    if (type === 'success') {
        messageDiv.style.backgroundColor = '#10b981';
    } else if (type === 'error') {
        messageDiv.style.backgroundColor = '#ef4444';
    } else {
        messageDiv.style.backgroundColor = '#3b82f6';
    }

    document.body.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => messageDiv.remove(), 300);
    }, 5000);
}

if (!document.getElementById('message-animations')) {
    const style = document.createElement('style');
    style.id = 'message-animations';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

class UserAPI {
    constructor() {
        this.baseURL = USER_API_BASE_URL;
    }

    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        const tokens = authAPI.getTokens();
        if (tokens.accessToken) {
            headers['Authorization'] = `Bearer ${tokens.accessToken}`;
        }
        
        return headers;
    }

    async request(endpoint, method = 'GET', data = null, isFormData = false, retryOn401 = true) {
        try {
            const options = {
                method: method,
                headers: this.getHeaders()
            };

            if (data) {
                if (isFormData) {
                    delete options.headers['Content-Type'];
                    options.body = data;
                } else if (method === 'POST' || method === 'PUT') {
                    options.body = JSON.stringify(data);
                }
            }

            const response = await fetch(`${this.baseURL}${endpoint}`, options);
            const result = await response.json();

            // Nếu nhận được 401 và có retryOn401, thử refresh token
            if (response.status === 401 && retryOn401) {
                const tokens = authAPI.getTokens();
                if (tokens.refreshToken) {
                    const refreshResult = await authAPI.refreshToken();
                    if (refreshResult.success) {
                        // Retry request với token mới (chỉ retry 1 lần)
                        return await this.request(endpoint, method, data, isFormData, false);
                    } else {
                        // Refresh thất bại, xóa tokens và redirect
                        authAPI.clearTokens();
                        return {
                            success: false,
                            data: null,
                            message: 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.',
                            errors: null,
                            pagination: null,
                            status: 401
                        };
                    }
                } else {
                    // Không có refresh token, xóa tokens
                    authAPI.clearTokens();
                    return {
                        success: false,
                        data: null,
                        message: 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.',
                        errors: null,
                        pagination: null,
                        status: 401
                    };
                }
            }

            return {
                success: result.success,
                data: result.data,
                message: result.message,
                errors: result.errors,
                pagination: result.pagination,
                status: response.status
            };
        } catch (error) {
            return {
                success: false,
                message: 'Lỗi kết nối đến server. Vui lòng thử lại sau.',
                error: error.message,
                status: 0
            };
        }
    }

    async getProfile() {
        return await this.request('/profile', 'GET');
    }

    async updateProfile(fullName, phone, address, idCard) {
        return await this.request('/profile', 'PUT', {
            full_name: fullName,
            phone: phone || null,
            address: address || null,
            id_card: idCard || null
        });
    }

    async changePassword(oldPassword, newPassword) {
        return await this.request('/change-password', 'PUT', {
            old_password: oldPassword,
            new_password: newPassword
        });
    }

    async uploadAvatar(file) {
        const formData = new FormData();
        formData.append('avatar', file);
        return await this.request('/upload-avatar', 'POST', formData, true);
    }

    async getBookings(page = 1, perPage = 10) {
        return await this.request(`/bookings?page=${page}&per_page=${perPage}`, 'GET');
    }

    async getFavorites(page = 1, perPage = 10) {
        return await this.request(`/favorites?page=${page}&per_page=${perPage}`, 'GET');
    }

    async getNotifications(page = 1, perPage = 20) {
        return await this.request(`/notifications?page=${page}&per_page=${perPage}`, 'GET');
    }

    async markNotificationRead(notificationId) {
        return await this.request(`/notifications/${notificationId}/read`, 'PUT');
    }

    async deleteNotification(notificationId) {
        return await this.request(`/notifications/${notificationId}`, 'DELETE');
    }
}

const userAPI = new UserAPI();
