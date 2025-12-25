<template>
  <div class="login-container">
    <header class="header">
      <h1>Веб-программирование, ЛР-2, Вариант-7654</h1>
      <p class="student-info">Смирнов Вадим Константинович, Р3219</p>
    </header>

    <main class="login-main">
      <div class="login-form-container">
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="input-group">
            <label for="login-input">Логин:</label>
            <input
              id="login-input"
              type="text"
              v-model="login"
              placeholder="Введите логин"
              class="text-input"
            />
          </div>

          <div class="input-group">
            <label for="password-input">Пароль:</label>
            <input
              id="password-input"
              type="password"
              v-model="password"
              placeholder="Введите пароль"
              class="text-input"
            />
          </div>

          <div class="error-message" v-if="error">{{ error }}</div>

          <button type="submit" class="login-button">
            Войти
          </button>
        </form>
      </div>
    </main>

    <footer class="footer">
      <p>ИТМО 2025</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'LoginPage',
  data() {
    return {
      login: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.error = ''
      
      if (!this.login || !this.password) {
        this.error = 'Заполните все поля'
        return
      }

      try {
        const response = await fetch('http://localhost:8080/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            login: this.login,
            password: this.password
          })
        })

        if (!response.ok) {
          const errorData = await response.json()
          this.error = errorData.errors ? Object.values(errorData.errors).join(', ') : 'Ошибка входа'
          return
        }

        const result = await response.json()
        
        if (result.success) {
          this.$router.push('/main')
        } else {
          this.error = result.message || 'Ошибка входа'
        }
      } catch (error) {
        console.error('Ошибка при отправке запроса:', error)
        this.error = 'Ошибка подключения к серверу. Убедитесь, что бэкенд запущен на http://localhost:8080'
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  margin-bottom: 50px;
  background-color: #8b5a9f;
  color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header h1 {
  color: white;
  font-size: 24px;
  margin-bottom: 10px;
}

.student-info {
  color: white;
  font-size: 16px;
}

.login-main {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-form-container {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}

.login-form {
  display: flex;
  flex-direction: column;
}

.input-group {
  margin-bottom: 25px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #3d2817;
}

.text-input {
  width: 100%;
  padding: 10px;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.text-input:focus {
  outline: none;
  border-color: #8b5a9f;
}

.login-button {
  width: 100%;
  padding: 15px;
  background-color: #8b5a9f;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 10px;
}

.login-button:hover {
  background-color: #7a4a8a;
}

.error-message {
  color: #d32f2f;
  font-size: 14px;
  margin-top: 10px;
  margin-bottom: 10px;
  text-align: center;
}

.footer {
  text-align: center;
  color: #3d2817;
  font-size: 14px;
  margin-top: auto;
  padding-top: 20px;
}

@media (min-width: 753px) and (max-width: 1078px) {
  .login-container {
    padding: 15px;
  }

  .header {
    padding: 15px;
    margin-bottom: 30px;
  }

  .header h1 {
    font-size: 20px;
  }

  .student-info {
    font-size: 14px;
  }

  .login-form-container {
    padding: 30px;
    max-width: 350px;
  }
}

@media (max-width: 752px) {
  .login-container {
    padding: 10px;
  }

  .header {
    padding: 15px;
    margin-bottom: 20px;
  }

  .header h1 {
    font-size: 18px;
    margin-bottom: 8px;
  }

  .student-info {
    font-size: 12px;
  }

  .login-main {
    padding: 10px 0;
  }

  .login-form-container {
    padding: 20px;
    max-width: 100%;
  }

  .input-group {
    margin-bottom: 20px;
  }

  .text-input {
    font-size: 14px;
    padding: 8px;
  }

  .login-button {
    padding: 12px;
    font-size: 16px;
  }

  .footer {
    font-size: 12px;
    padding-top: 15px;
  }
}
</style>

