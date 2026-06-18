import { useCallback, useEffect, useMemo, useState } from 'react'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const TOKEN_STORAGE_KEY = 'task_manager_access_token'
const USER_STORAGE_KEY = 'task_manager_user'
const EMPTY_TASK_FORM = {
  title: '',
  description: '',
  category: 'general',
}

function App() {
  const [authMode, setAuthMode] = useState('login')
  const [authForm, setAuthForm] = useState({ username: '', password: '' })
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_STORAGE_KEY) || '')
  const [user, setUser] = useState(() => readStoredUser())
  const [tasks, setTasks] = useState([])
  const [taskForm, setTaskForm] = useState(EMPTY_TASK_FORM)
  const [editingTaskId, setEditingTaskId] = useState(null)
  const [editForm, setEditForm] = useState({ ...EMPTY_TASK_FORM, status: 'pending' })
  const [filters, setFilters] = useState({ status: 'all', category: 'all' })
  const [isAuthLoading, setIsAuthLoading] = useState(false)
  const [isTasksLoading, setIsTasksLoading] = useState(false)
  const [isSavingTask, setIsSavingTask] = useState(false)
  const [activeTaskId, setActiveTaskId] = useState(null)
  const [message, setMessage] = useState({ type: '', text: '' })

  const isAuthenticated = Boolean(token)

  const categories = useMemo(() => {
    const uniqueCategories = new Set(tasks.map((task) => task.category).filter(Boolean))
    return Array.from(uniqueCategories).sort((first, second) => first.localeCompare(second))
  }, [tasks])

  const stats = useMemo(() => {
    const total = tasks.length
    const completed = tasks.filter((task) => task.status === 'completed').length
    const pending = total - completed
    const completionRate = total === 0 ? 0 : Math.round((completed / total) * 100)

    return { total, completed, pending, completionRate }
  }, [tasks])

  const clearSession = useCallback(() => {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    localStorage.removeItem(USER_STORAGE_KEY)
    setToken('')
    setUser(null)
    setTasks([])
    setEditingTaskId(null)
  }, [])

  const handleApiError = useCallback(
    (error, fallbackMessage) => {
      // This API uses 401 and 422 when credentials or tokens are invalid or unusable.
      if (error.status === 401 || error.status === 422) {
        clearSession()
      }

      setMessage({
        type: 'error',
        text: error.details ? `${error.message}: ${error.details}` : error.message || fallbackMessage,
      })
    },
    [clearSession],
  )

  const request = useCallback(async (endpoint, options = {}) => {
    const headers = {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    })

    const data = await parseJson(response)

    if (!response.ok) {
      const errorMessage = data?.error || data?.message || 'Something went wrong'
      const error = new Error(errorMessage)
      error.status = response.status
      error.details = data?.details
      throw error
    }

    return data
  }, [token])

  const fetchTasks = useCallback(async () => {
    setIsTasksLoading(true)
    setMessage({ type: '', text: '' })

    try {
      const params = new URLSearchParams()

      if (filters.status !== 'all') {
        params.set('status', filters.status)
      }

      if (filters.category !== 'all') {
        params.set('category', filters.category)
      }

      const query = params.toString()
      const data = await request(`/tasks${query ? `?${query}` : ''}`)
      setTasks(data)
    } catch (error) {
      handleApiError(error, 'Could not load tasks.')
    } finally {
      setIsTasksLoading(false)
    }
  }, [filters.category, filters.status, handleApiError, request])

  useEffect(() => {
    if (token) {
      const timeoutId = window.setTimeout(fetchTasks, 0)

      return () => window.clearTimeout(timeoutId)
    }
  }, [fetchTasks, token])

  async function handleAuthSubmit(event) {
    event.preventDefault()
    setIsAuthLoading(true)
    setMessage({ type: '', text: '' })

    try {
      if (authMode === 'register') {
        await request('/register', {
          method: 'POST',
          body: JSON.stringify(authForm),
        })
      }

      const loginData = await request('/login', {
        method: 'POST',
        body: JSON.stringify(authForm),
      })

      localStorage.setItem(TOKEN_STORAGE_KEY, loginData.access_token)
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(loginData.user))
      setToken(loginData.access_token)
      setUser(loginData.user)
      setAuthForm({ username: '', password: '' })
      setMessage({
        type: 'success',
        text: authMode === 'register' ? 'Account created and signed in.' : 'Signed in successfully.',
      })
    } catch (error) {
      handleApiError(error, authMode === 'register' ? 'Registration failed.' : 'Login failed.')
    } finally {
      setIsAuthLoading(false)
    }
  }

  async function handleLogout() {
    setActiveTaskId('logout')
    setMessage({ type: '', text: '' })

    try {
      await request('/logout', { method: 'DELETE' })
      setMessage({ type: 'success', text: 'Signed out successfully.' })
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.message || 'The session was cleared locally.',
      })
    } finally {
      // Always end the browser session locally, even if server-side token revocation fails.
      clearSession()
      setActiveTaskId(null)
    }
  }

  async function handleCreateTask(event) {
    event.preventDefault()
    setIsSavingTask(true)
    setMessage({ type: '', text: '' })

    try {
      await request('/tasks', {
        method: 'POST',
        body: JSON.stringify(taskForm),
      })
      setTaskForm(EMPTY_TASK_FORM)
      setMessage({ type: 'success', text: 'Task created.' })
      await fetchTasks()
    } catch (error) {
      handleApiError(error, 'Could not create task.')
    } finally {
      setIsSavingTask(false)
    }
  }

  async function handleUpdateTask(taskId, updates, successText = 'Task updated.') {
    setActiveTaskId(taskId)
    setMessage({ type: '', text: '' })

    try {
      await request(`/tasks/${taskId}`, {
        method: 'PUT',
        body: JSON.stringify(updates),
      })
      setMessage({ type: 'success', text: successText })
      await fetchTasks()
      setEditingTaskId(null)
    } catch (error) {
      handleApiError(error, 'Could not update task.')
    } finally {
      setActiveTaskId(null)
    }
  }

  async function handleDeleteTask(taskId) {
    const shouldDelete = window.confirm('Delete this task? This action cannot be undone.')

    if (!shouldDelete) {
      return
    }

    setActiveTaskId(taskId)
    setMessage({ type: '', text: '' })

    try {
      await request(`/tasks/${taskId}`, { method: 'DELETE' })
      setMessage({ type: 'success', text: 'Task deleted.' })
      await fetchTasks()
    } catch (error) {
      handleApiError(error, 'Could not delete task.')
    } finally {
      setActiveTaskId(null)
    }
  }

  function startEditing(task) {
    setEditingTaskId(task.id)
    setEditForm({
      title: task.title,
      description: task.description,
      category: task.category,
      status: task.status,
    })
  }

  function submitEdit(event, taskId) {
    event.preventDefault()
    handleUpdateTask(taskId, editForm, 'Task saved.')
  }

  function toggleTaskStatus(task) {
    const nextStatus = task.status === 'completed' ? 'pending' : 'completed'
    handleUpdateTask(task.id, { status: nextStatus }, `Marked as ${nextStatus}.`)
  }

  if (!isAuthenticated) {
    return (
      <main className="auth-page">
        <section className="auth-panel" aria-labelledby="auth-title">
          <div className="brand-block">
            <p className="eyebrow">Task Manager API</p>
            <h1 id="auth-title">Organize every task in one clean workspace.</h1>
            <p className="intro">
              Sign in or create an account to manage private tasks with the existing Flask API.
            </p>
          </div>

          <form className="auth-card" onSubmit={handleAuthSubmit}>
            <div className="switcher" role="tablist" aria-label="Authentication mode">
              <button
                type="button"
                className={authMode === 'login' ? 'active' : ''}
                onClick={() => setAuthMode('login')}
              >
                Login
              </button>
              <button
                type="button"
                className={authMode === 'register' ? 'active' : ''}
                onClick={() => setAuthMode('register')}
              >
                Register
              </button>
            </div>

            <label>
              Username
              <input
                value={authForm.username}
                onChange={(event) => setAuthForm({ ...authForm, username: event.target.value })}
                minLength="3"
                autoComplete="username"
                required
              />
            </label>

            <label>
              Password
              <input
                type="password"
                value={authForm.password}
                onChange={(event) => setAuthForm({ ...authForm, password: event.target.value })}
                minLength="6"
                autoComplete={authMode === 'login' ? 'current-password' : 'new-password'}
                required
              />
            </label>

            <button className="primary-button" type="submit" disabled={isAuthLoading}>
              {isAuthLoading ? 'Please wait...' : authMode === 'login' ? 'Login' : 'Create account'}
            </button>

            <StatusMessage message={message} />
          </form>
        </section>
      </main>
    )
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Private workspace</p>
          <h1>Task dashboard</h1>
        </div>
        <div className="user-actions">
          <span>{user?.username}</span>
          <button type="button" className="ghost-button" onClick={handleLogout} disabled={activeTaskId === 'logout'}>
            {activeTaskId === 'logout' ? 'Signing out...' : 'Logout'}
          </button>
        </div>
      </header>

      <StatusMessage message={message} />

      <section className="stats-grid" aria-label="Task statistics">
        <StatCard label="Total" value={stats.total} />
        <StatCard label="Pending" value={stats.pending} />
        <StatCard label="Completed" value={stats.completed} />
        <StatCard label="Completion" value={`${stats.completionRate}%`} />
      </section>

      <section className="workspace">
        <aside className="sidebar">
          <form className="panel" onSubmit={handleCreateTask}>
            <div className="panel-heading">
              <h2>Create task</h2>
              <p>Add a task to your personal list.</p>
            </div>

            <TaskFields form={taskForm} onChange={setTaskForm} />

            <button className="primary-button" type="submit" disabled={isSavingTask}>
              {isSavingTask ? 'Creating...' : 'Create task'}
            </button>
          </form>

          <div className="panel">
            <div className="panel-heading">
              <h2>Filters</h2>
              <p>Narrow the list by status or category.</p>
            </div>

            <label>
              Status
              <select
                value={filters.status}
                onChange={(event) => setFilters({ ...filters, status: event.target.value })}
              >
                <option value="all">All statuses</option>
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
              </select>
            </label>

            <label>
              Category
              <select
                value={filters.category}
                onChange={(event) => setFilters({ ...filters, category: event.target.value })}
              >
                <option value="all">All categories</option>
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </aside>

        <section className="tasks-panel" aria-labelledby="tasks-title">
          <div className="tasks-header">
            <div>
              <h2 id="tasks-title">Tasks</h2>
              <p>{isTasksLoading ? 'Loading tasks...' : `${tasks.length} task${tasks.length === 1 ? '' : 's'} shown`}</p>
            </div>
            <button type="button" className="ghost-button" onClick={fetchTasks} disabled={isTasksLoading}>
              Refresh
            </button>
          </div>

          {isTasksLoading ? (
            <div className="empty-state">Loading your tasks...</div>
          ) : tasks.length === 0 ? (
            <div className="empty-state">No tasks match the current view.</div>
          ) : (
            <div className="task-list">
              {tasks.map((task) => (
                <article className={`task-card ${task.status}`} key={task.id}>
                  {editingTaskId === task.id ? (
                    <form className="edit-form" onSubmit={(event) => submitEdit(event, task.id)}>
                      <TaskFields form={editForm} onChange={setEditForm} includeStatus />
                      <div className="task-actions">
                        <button className="primary-button compact" type="submit" disabled={activeTaskId === task.id}>
                          {activeTaskId === task.id ? 'Saving...' : 'Save'}
                        </button>
                        <button type="button" className="ghost-button compact" onClick={() => setEditingTaskId(null)}>
                          Cancel
                        </button>
                      </div>
                    </form>
                  ) : (
                    <>
                      <div className="task-content">
                        <div>
                          <span className="status-pill">{task.status}</span>
                          <h3>{task.title}</h3>
                        </div>
                        <p>{task.description || 'No description provided.'}</p>
                        <span className="category-chip">{task.category}</span>
                      </div>

                      <div className="task-actions">
                        <button
                          type="button"
                          className="secondary-button compact"
                          onClick={() => toggleTaskStatus(task)}
                          disabled={activeTaskId === task.id}
                        >
                          {task.status === 'completed' ? 'Mark pending' : 'Mark completed'}
                        </button>
                        <button type="button" className="ghost-button compact" onClick={() => startEditing(task)}>
                          Edit
                        </button>
                        <button
                          type="button"
                          className="danger-button compact"
                          onClick={() => handleDeleteTask(task.id)}
                          disabled={activeTaskId === task.id}
                        >
                          Delete
                        </button>
                      </div>
                    </>
                  )}
                </article>
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  )
}

function TaskFields({ form, onChange, includeStatus = false }) {
  return (
    <div className="field-stack">
      <label>
        Title
        <input
          value={form.title}
          onChange={(event) => onChange({ ...form, title: event.target.value })}
          placeholder="Write API docs"
          required
        />
      </label>

      <label>
        Description
        <textarea
          value={form.description}
          onChange={(event) => onChange({ ...form, description: event.target.value })}
          placeholder="Add useful details"
          rows="4"
        />
      </label>

      <label>
        Category
        <input
          value={form.category}
          onChange={(event) => onChange({ ...form, category: event.target.value })}
          placeholder="general"
        />
      </label>

      {includeStatus ? (
        <label>
          Status
          <select value={form.status} onChange={(event) => onChange({ ...form, status: event.target.value })}>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>
        </label>
      ) : null}
    </div>
  )
}

function StatCard({ label, value }) {
  return (
    <div className="stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function StatusMessage({ message }) {
  if (!message.text) {
    return null
  }

  return (
    <div className={`status-message ${message.type}`} role="status">
      {message.text}
    </div>
  )
}

async function parseJson(response) {
  const text = await response.text()

  if (!text) {
    return null
  }

  return JSON.parse(text)
}

function readStoredUser() {
  const storedUser = localStorage.getItem(USER_STORAGE_KEY)

  if (!storedUser) {
    return null
  }

  try {
    return JSON.parse(storedUser)
  } catch {
    localStorage.removeItem(USER_STORAGE_KEY)
    return null
  }
}

export default App
