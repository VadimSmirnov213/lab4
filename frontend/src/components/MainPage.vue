<template>
  <div class="app-container">
    <header class="header">
      <h1>Веб-программирование, ЛР-4, Вариант-7654</h1>
      <p class="student-info">Смирнов Вадим Константинович, Р3219</p>
    </header>

    <main class="main-content">
      <div class="input-section">
        <div class="input-group">
          <label for="x-input">Введите X:</label>
          <input
            id="x-input"
            type="text"
            v-model.number="x"
            placeholder="от -5 до 5"
            class="text-input"
          />
        </div>

        <div class="input-group">
          <label for="y-input">Введите Y:</label>
          <input
            id="y-input"
            type="text"
            v-model.number="y"
            placeholder="от -5 до 3"
            class="text-input"
          />
        </div>

        <div class="input-group">
          <label for="r-input">Введите R:</label>
          <input
            id="r-input"
            type="text"
            v-model.number="r"
            placeholder="от -5 до 5"
            class="text-input"
          />
        </div>

        <div class="error-message" v-if="serverError">{{ serverError }}</div>

        <button @click="checkPoint" class="check-button" :disabled="!isFormFilled">
          ПРОВЕРИТЬ
        </button>
        
        <button @click="goBack" class="back-button">
          НАЗАД
        </button>
      </div>

      <div class="graph-section">
        <GraphComponent :r="r" :points="points" @point-click="handlePointClick" />
      </div>
    </main>

    <div class="results-section">
      <h2>Результаты</h2>
      <table class="results-table">
        <thead>
          <tr>
            <th>X</th>
            <th>Y</th>
            <th>R</th>
            <th>Время</th>
            <th>Рез.</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(result, index) in results" :key="index">
            <td>{{ result.x }}</td>
            <td>{{ result.y }}</td>
            <td>{{ result.r }}</td>
            <td>{{ result.time }}</td>
            <td :class="{ 'hit': result.hit, 'miss': !result.hit }">
              {{ result.hit ? 'Попадание' : 'Промах' }}
            </td>
          </tr>
          <tr v-if="results.length === 0">
            <td colspan="5" class="empty-message">Нет результатов</td>
          </tr>
        </tbody>
      </table>
    </div>

    <footer class="footer">
      <p>ИТМО 2025</p>
    </footer>
  </div>
</template>

<script>
import GraphComponent from './GraphComponent.vue'

export default {
  name: 'MainPage',
  components: {
    GraphComponent
  },
  data() {
    return {
      x: null,
      y: null,
      r: null,
      results: [],
      points: [],
      serverError: null
    }
  },
  computed: {
    isFormFilled() {
      return this.x !== null && this.y !== null && this.r !== null &&
             this.x !== '' && this.y !== '' && this.r !== ''
    }
  },
  async mounted() {
    await this.loadPoints()
  },
  methods: {
    getAuthToken() {
      return localStorage.getItem('authToken')
    },
    clearAuthToken() {
      localStorage.removeItem('authToken')
    },
    getAuthHeaders() {
      const token = this.getAuthToken()
      const headers = {
        'Content-Type': 'application/json',
      }
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
      return headers
    },
    async loadPoints() {
      const token = this.getAuthToken()
      if (!token) {
        this.$router.push('/')
        return
      }

      try {
        const response = await fetch('http://localhost:8080/api/points', {
          method: 'GET',
          headers: this.getAuthHeaders()
        })

        if (response.ok) {
          const points = await response.json()
          this.results = points.map(point => {
            let formattedTime = point.time
            if (point.time) {
              try {
                formattedTime = new Date(point.time).toLocaleString('ru-RU')
              } catch (e) {
                formattedTime = point.time
              }
            }
            return {
              x: point.x,
              y: point.y,
              r: point.r,
              time: formattedTime,
              hit: point.hit
            }
          })
          this.points = points.map(point => ({
            x: point.x,
            y: point.y,
            hit: point.hit
          }))
        } else if (response.status === 401) {
          this.clearAuthToken()
          this.$router.push('/')
        }
      } catch (error) {
        console.error('Ошибка при загрузке точек:', error)
      }
    },
    async checkPoint() {
      if (!this.isFormFilled) return
      
      this.serverError = null
      
      const token = this.getAuthToken()
      if (!token) {
        this.serverError = 'Требуется авторизация. Пожалуйста, войдите в систему.'
        this.$router.push('/')
        return
      }

      try {
        const response = await fetch('http://localhost:8080/api/check', {
          method: 'POST',
          headers: this.getAuthHeaders(),
          body: JSON.stringify({
            x: Number(this.x),
            y: Number(this.y),
            r: Number(this.r)
          })
        })

        if (!response.ok) {
          let errorMessage = 'Неизвестная ошибка'
          try {
            const errorData = await response.json()
            console.error('Ошибка:', errorData)
            if (errorData.errors) {
              errorMessage = Object.values(errorData.errors).join(', ')
            } else if (errorData.error) {
              errorMessage = errorData.error
            } else if (errorData.message) {
              errorMessage = errorData.message
            }
          } catch (e) {
            if (response.status === 401) {
              this.clearAuthToken()
              this.$router.push('/')
              errorMessage = 'Требуется авторизация. Пожалуйста, войдите в систему.'
            } else if (response.status === 400) {
              errorMessage = 'Некорректные данные'
            } else {
              errorMessage = `Ошибка сервера: ${response.status}`
            }
          }
          this.serverError = errorMessage
          return
        }

        const result = await response.json()
        
        let formattedTime = result.time
        if (result.time) {
          try {
            formattedTime = new Date(result.time).toLocaleString('ru-RU')
          } catch (e) {
            formattedTime = result.time
          }
        }
        
        this.results.unshift({
          x: result.x,
          y: result.y,
          r: result.r,
          time: formattedTime,
          hit: result.hit
        })
        
        this.points.push({ 
          x: result.x, 
          y: result.y, 
          hit: result.hit 
        })
      } catch (error) {
        console.error('Ошибка при отправке запроса:', error)
        alert('Ошибка подключения к серверу. Убедитесь, что бэкенд запущен на http://localhost:8080')
      }
    },
    handlePointClick(x, y) {
      this.x = x
      this.y = y
    },
    async goBack() {
      try {
        const token = this.getAuthToken()
        if (token) {
          await fetch('http://localhost:8080/api/points', {
            method: 'DELETE',
            headers: this.getAuthHeaders()
          })
        }
      } catch (error) {
        console.error('Ошибка при выходе:', error)
      }
      
      this.clearAuthToken()
      this.results = []
      this.points = []
      this.x = null
      this.y = null
      this.r = null
      
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  margin-bottom: 30px;
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

.main-content {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
  flex: 1;
}

.input-section {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  flex: 1;
  max-width: 400px;
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

.error-message {
  color: #d32f2f;
  font-size: 12px;
  margin-top: 5px;
}

.check-button {
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
  margin-top: 20px;
}

.check-button:hover:not(:disabled) {
  background-color: #7a4a8a;
}

.check-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.back-button {
  width: 100%;
  padding: 15px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 10px;
}

.back-button:hover {
  background-color: #5a6268;
}

.graph-section {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  flex: 1;
}

.results-section {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.results-section h2 {
  margin-bottom: 15px;
  color: #3d2817;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
}

.results-table th,
.results-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.results-table th {
  background-color: #f5f5f5;
  font-weight: 600;
  color: #3d2817;
}

.results-table .hit {
  color: #2e7d32;
  font-weight: 600;
}

.results-table .miss {
  color: #d32f2f;
  font-weight: 600;
}

.empty-message {
  text-align: center;
  color: #999;
  font-style: italic;
}

.footer {
  text-align: center;
  color: #3d2817;
  font-size: 14px;
  margin-top: auto;
  padding-top: 20px;
}

@media (min-width: 753px) and (max-width: 1078px) {
  .app-container {
    padding: 15px;
  }

  .header {
    padding: 15px;
    margin-bottom: 20px;
  }

  .header h1 {
    font-size: 20px;
  }

  .student-info {
    font-size: 14px;
  }

  .main-content {
    flex-direction: column;
    gap: 20px;
  }

  .input-section {
    max-width: 100%;
    padding: 20px;
  }

  .graph-section {
    padding: 20px;
  }

  .results-section {
    padding: 20px;
  }

  .results-table th,
  .results-table td {
    padding: 10px;
    font-size: 14px;
  }
}

@media (max-width: 752px) {
  .app-container {
    padding: 10px;
  }

  .header {
    padding: 15px;
    margin-bottom: 15px;
  }

  .header h1 {
    font-size: 16px;
    margin-bottom: 8px;
  }

  .student-info {
    font-size: 12px;
  }

  .main-content {
    flex-direction: column;
    gap: 15px;
    margin-bottom: 20px;
  }

  .input-section {
    max-width: 100%;
    padding: 15px;
  }

  .input-group {
    margin-bottom: 15px;
  }

  .input-group label {
    font-size: 14px;
    margin-bottom: 6px;
  }

  .text-input {
    font-size: 14px;
    padding: 8px;
  }

  .check-button {
    padding: 12px;
    font-size: 16px;
    margin-top: 15px;
  }

  .graph-section {
    padding: 15px;
  }

  .results-section {
    padding: 15px;
    margin-bottom: 15px;
  }

  .results-section h2 {
    font-size: 18px;
    margin-bottom: 10px;
  }

  .results-table {
    font-size: 12px;
  }

  .results-table th,
  .results-table td {
    padding: 8px;
    font-size: 12px;
  }

  .footer {
    font-size: 12px;
    padding-top: 15px;
  }
}
</style>

