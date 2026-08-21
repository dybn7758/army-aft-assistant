import {useEffect, useState } from 'react'
import './App.css'

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'

function App() {
  const [activeTab, setActiveTab] = useState('chat')

  // Chat state
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  // Calculator state
  const [age, setAge] = useState('')
  const [gender, setGender] = useState('male')
  const [event, setEvent] = useState('mdl')
  const [performance, setPerformance] = useState('')
  const [standardType, setStandardType] = useState('general')

  const [scoreResult, setScoreResult] = useState(null)
  const [scoreError, setScoreError] = useState('')
  const [scoreLoading, setScoreLoading] = useState(false)

  // Session state
  const [sessionId] = useState(() => crypto.randomUUID())

  // Soldier profile state persisted in localStorage
  const [username, setUsername] = useState(
    () => localStorage.getItem('aftUsername') || ''
  )

  const [birthDate, setBirthDate] = useState(
    () => localStorage.getItem('aftBirthDate') || ''
  )

  const [profileGender, setProfileGender] = useState(
    () => localStorage.getItem('aftGender') || 'male'
  )

  const [component, setComponent] = useState(
    () => localStorage.getItem('aftComponent') || ''
  )

  const [mos, setMos] = useState(
    () => localStorage.getItem('aftMos') || ''
  )

  const [userId, setUserId] = useState(() => {
    const savedUserId = localStorage.getItem('aftUserId')

    return savedUserId
      ? Number(savedUserId)
      : null
  })


   useEffect(() => {
    if (userId) {
      loadProfile(userId)
      loadAftHistory()
    }
  }, [userId])

  const [profileMessage, setProfileMessage] = useState('')

  // Full AFT test state
  const [testDate, setTestDate] = useState('')
  const [testStandardType, setTestStandardType] = useState('general')

  const [deadliftPerformance, setDeadliftPerformance] = useState('')
  const [hrpPerformance, setHrpPerformance] = useState('')
  const [sdcPerformance, setSdcPerformance] = useState('')
  const [plankPerformance, setPlankPerformance] = useState('')
  const [twoMileRunPerformance, setTwoMileRunPerformance] = useState('')

  const [aftHistory, setAftHistory] = useState([])
  const [aftMessage, setAftMessage] = useState('')
  const [aftLoading, setAftLoading] = useState(false)

  // progress dashboard state
  const chartData = aftHistory.map((test) => ({
    date: test.test_date,
    score: test.total_score,
  }))

  async function loadProfile(userId) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/users/${userId}`
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.error || 'Unable to load profile'
        )
      }

      setUsername(data.username)
      setBirthDate(data.birth_date)
      setProfileGender(data.gender)
      setComponent(data.component || '')
      setMos(data.mos || '')
    } catch (error) {
      console.error(error)

      clearProfile()
    }
  }

 

  async function sendMessage() {
    if (!userId) {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: 'assistant',
          content: 'Please create a Soldier profile first.',
        },
      ])

      return
    }

    if (!message.trim() || loading) {
      return
    }

    const userMessage = message

    setMessages((currentMessages) => [
      ...currentMessages,
      {
        role: 'user',
        content: userMessage,
      },
    ])

    setMessage('')
    setLoading(true)

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/chat`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: userMessage,
            user_id: userId,
            session_id: sessionId,
          }),
        }
      )

      // Read the response as text first.
      const responseText = await response.text()

      let data = {}

      // Only try to parse JSON if there is a response body.
      if (responseText) {
        try {
          data = JSON.parse(responseText)
        } catch {
          throw new Error(
            `Backend returned invalid JSON: ${responseText}`
          )
        }
      }

      // response is defined here because we are still
      // inside the same try block.
      if (!response.ok) {
        throw new Error(
          data.error ||
          `Backend request failed with status ${response.status}`
        )
      }

      if (!data.answer) {
        throw new Error(
          'Backend returned an empty response.'
        )
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: 'assistant',
          content: data.answer,
        },
      ])
    } catch (error) {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: 'assistant',
          content: `Error: ${error.message}`,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  async function calculateScore() {
    if (!age || !performance) {
      setScoreError('Age and performance are required.')
      return
    }

    setScoreLoading(true)
    setScoreError('')
    setScoreResult(null)

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/aft/calculate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            age: Number(age),
            gender,
            event,
            performance,
            standard_type: standardType,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.error || 'Unable to calculate score'
        )
      }

      setScoreResult(data)
    } catch (error) {
      setScoreError(error.message)
    } finally {
      setScoreLoading(false)
    }
  }

  async function createProfile() {
    setProfileMessage('')

    if (!username || !birthDate || !profileGender) {
      setProfileMessage(
        'Username, birth date, and gender are required.'
      )
      return
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/users`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username,
            birth_date: birthDate,
            gender: profileGender,
            component,
            mos,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.error || 'Unable to create profile'
        )
      }

      setUserId(data.id)

      localStorage.setItem(
        'aftUserId',
        String(data.id)
      )

      localStorage.setItem(
        'aftUsername',
        username
      )

      localStorage.setItem(
        'aftBirthDate',
        birthDate
      )

      localStorage.setItem(
        'aftGender',
        profileGender
      )

      localStorage.setItem(
        'aftComponent',
        component
      )

      localStorage.setItem(
        'aftMos',
        mos
      )

      setProfileMessage(
        `Profile created successfully. User ID: ${data.id}`
      )
    } catch (error) {
      setProfileMessage(error.message)
    }
  }

  function clearProfile() {
    setUserId(null)
    setUsername('')
    setBirthDate('')
    setProfileGender('male')
    setComponent('')
    setMos('')
    setMessages([])
    setAftHistory([])
    setProfileMessage('')
    setAftMessage('')

    localStorage.removeItem('aftUserId')
    localStorage.removeItem('aftUsername')
    localStorage.removeItem('aftBirthDate')
    localStorage.removeItem('aftGender')
    localStorage.removeItem('aftComponent')
    localStorage.removeItem('aftMos')
  }



  async function saveAftTest() {
    if (!userId) {
      setAftMessage('Please create a Soldier profile first.')
      return
    }

    if (
      !testDate ||
      !deadliftPerformance ||
      !hrpPerformance ||
      !sdcPerformance ||
      !plankPerformance ||
      !twoMileRunPerformance
    ) {
      setAftMessage(
        'Please complete all AFT performance fields.'
      )
      return
    }

    setAftLoading(true)
    setAftMessage('')

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/aft-scores`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: userId,
            test_date: testDate,
            standard_type: testStandardType,
            deadlift_performance: Number(deadliftPerformance),
            hrp_performance: Number(hrpPerformance),
            sdc_performance: sdcPerformance,
            plank_performance: plankPerformance,
            two_mile_run_performance: twoMileRunPerformance,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.error || 'Unable to save AFT test'
        )
      }

      setAftMessage(
        `AFT test saved. Total score: ${data.total_score}`
      )

      setDeadliftPerformance('')
      setHrpPerformance('')
      setSdcPerformance('')
      setPlankPerformance('')
      setTwoMileRunPerformance('')

      await loadAftHistory()
    } catch (error) {
      setAftMessage(error.message)
    } finally {
      setAftLoading(false)
    }
  }

  async function loadAftHistory() {
    if (!userId) {
      setAftMessage('Please create a Soldier profile first.')
      return
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/aft-scores/${userId}`
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.error || 'Unable to load AFT history'
        )
      }

      setAftHistory(data)
    } catch (error) {
      setAftMessage(error.message)
    }
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter') {
      sendMessage()
    }
  }

  function getPerformancePlaceholder() {
    if (event === 'mdl') {
      return 'Weight in pounds, e.g. 250'
    }

    if (event === 'hrp') {
      return 'Number of repetitions, e.g. 40'
    }

    return 'Time in MM:SS, e.g. 2:30'
  }

  const latestTest =
    aftHistory.length > 0
      ? aftHistory[aftHistory.length - 1]
      : null

  const previousTest =
    aftHistory.length > 1
      ? aftHistory[aftHistory.length - 2]
      : null

  const scoreChange =
    latestTest && previousTest
      ? latestTest.total_score - previousTest.total_score
      : null

  return (
    <main className="app">
      <header>
        <h1>Army AFT Assistant</h1>

        <p>
          Army Fitness Test information, scoring, Soldier profiles,
          and test history.
        </p>
      </header>

      <nav className="tabs">
        <button
          type="button"
          className={activeTab === 'chat' ? 'active' : ''}
          onClick={() => setActiveTab('chat')}
        >
          Chat
        </button>

        <button
          type="button"
          className={activeTab === 'calculator' ? 'active' : ''}
          onClick={() => setActiveTab('calculator')}
        >
          Score Calculator
        </button>

        <button
          type="button"
          className={activeTab === 'profile' ? 'active' : ''}
          onClick={() => setActiveTab('profile')}
        >
          Soldier Profile
        </button>

        <button
          type="button"
          className={activeTab === 'tests' ? 'active' : ''}
          onClick={() => {
            setActiveTab('tests')

            if (userId) {
              loadAftHistory()
            }
          }}
        >
          AFT Tests
        </button>

        <button
          type="button"
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          Progress Dashboard
        </button>
      </nav>

      {activeTab === 'chat' && (
        <>
          <section className="chat">
            {messages.length === 0 && (
              <p className="welcome">
                Ask me a question about the Army AFT.
              </p>
            )}

            {messages.map((chatMessage, index) => (
              <div
                key={index}
                className={`message ${chatMessage.role}`}
              >
                <strong>
                  {chatMessage.role === 'user'
                    ? 'You'
                    : 'AFT Assistant'}
                </strong>

                <p>{chatMessage.content}</p>
              </div>
            ))}

            {loading && (
              <div className="message assistant">
                <strong>AFT Assistant</strong>
                <p>Thinking...</p>
              </div>
            )}
          </section>

          <section className="input-area">
            <input
              type="text"
              value={message}
              placeholder={
                userId
                  ? 'Ask an AFT question...'
                  : 'Create a Soldier profile first...'
              }
              onChange={(event) =>
                setMessage(event.target.value)
              }
              onKeyDown={handleKeyDown}
            />

            <button
              type="button"
              onClick={sendMessage}
              disabled={loading}
            >
              Send
            </button>
          </section>

          {userId && (
            <p>
              Active Soldier: {username} | User ID: {userId}
            </p>
          )}
        </>
      )}

      {activeTab === 'calculator' && (
        <section className="calculator">
          <h2>AFT Score Calculator</h2>

          <div className="form-group">
            <label htmlFor="age">Age</label>

            <input
              id="age"
              type="number"
              value={age}
              onChange={(event) =>
                setAge(event.target.value)
              }
              placeholder="Enter age"
            />
          </div>

          <div className="form-group">
            <label htmlFor="gender">
              Gender
            </label>

            <select
              id="gender"
              value={gender}
              onChange={(event) =>
                setGender(event.target.value)
              }
            >
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="event">
              Event
            </label>

            <select
              id="event"
              value={event}
              onChange={(event) =>
                setEvent(event.target.value)
              }
            >
              <option value="mdl">
                3-Repetition Maximum Deadlift
              </option>

              <option value="hrp">
                Hand-Release Push-Up
              </option>

              <option value="sdc">
                Sprint-Drag-Carry
              </option>

              <option value="plank">
                Plank
              </option>

              <option value="two_mile_run">
                Two-Mile Run
              </option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="performance">
              Performance
            </label>

            <input
              id="performance"
              type="text"
              value={performance}
              onChange={(event) =>
                setPerformance(event.target.value)
              }
              placeholder={getPerformancePlaceholder()}
            />
          </div>

          <div className="form-group">
            <label htmlFor="standardType">
              Standard Type
            </label>

            <select
              id="standardType"
              value={standardType}
              onChange={(event) =>
                setStandardType(event.target.value)
              }
            >
              <option value="general">
                General
              </option>

              <option value="combat">
                Combat
              </option>
            </select>
          </div>

          <button
            type="button"
            onClick={calculateScore}
            disabled={scoreLoading}
          >
            {scoreLoading
              ? 'Calculating...'
              : 'Calculate Score'}
          </button>

          {scoreError && (
            <p className="error">
              {scoreError}
            </p>
          )}

          {scoreResult && (
            <div className="score-result">
              <h3>Result</h3>

              <p>
                <strong>Age Group:</strong>{' '}
                {scoreResult.age_group}
              </p>

              <p>
                <strong>Event:</strong>{' '}
                {scoreResult.event}
              </p>

              <p>
                <strong>Performance:</strong>{' '}
                {scoreResult.performance}
              </p>

              <p>
                <strong>Score:</strong>{' '}
                {scoreResult.score}
              </p>
            </div>
          )}
        </section>
      )}

      {activeTab === 'profile' && (
        <section className="calculator">
          <h2>Soldier Profile</h2>

          <div className="form-group">
            <label htmlFor="username">
              Username
            </label>

            <input
              id="username"
              type="text"
              value={username}
              onChange={(event) =>
                setUsername(event.target.value)
              }
              placeholder="Enter username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="birthDate">
              Birth Date
            </label>

            <input
              id="birthDate"
              type="date"
              value={birthDate}
              onChange={(event) =>
                setBirthDate(event.target.value)
              }
            />
          </div>

          <div className="form-group">
            <label htmlFor="profileGender">
              Gender
            </label>

            <select
              id="profileGender"
              value={profileGender}
              onChange={(event) =>
                setProfileGender(event.target.value)
              }
            >
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="component">
              Component
            </label>

            <select
              id="component"
              value={component}
              onChange={(event) =>
                setComponent(event.target.value)
              }
            >
              <option value="">
                Select component
              </option>

              <option value="Active Duty">
                Active Duty
              </option>

              <option value="Army Reserve">
                Army Reserve
              </option>

              <option value="Army National Guard">
                Army National Guard
              </option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="mos">
              MOS
            </label>

            <input
              id="mos"
              type="text"
              value={mos}
              onChange={(event) =>
                setMos(event.target.value)
              }
              placeholder="Example: 68G"
            />
          </div>

          {!userId && (
            <button
              type="button"
              onClick={createProfile}
            >
              Create Profile
            </button>
          )}

          {profileMessage && (
            <p>
              {profileMessage}
            </p>
          )}

          {userId && (
            <>
              <div className="score-result">
                <h3>Profile Active</h3>

                <p>
                  <strong>Username:</strong>{' '}
                  {username}
                </p>

                <p>
                  <strong>User ID:</strong>{' '}
                  {userId}
                </p>

                <p>
                  <strong>Birth Date:</strong>{' '}
                  {birthDate}
                </p>

                <p>
                  <strong>Gender:</strong>{' '}
                  {profileGender}
                </p>

                <p>
                  <strong>Component:</strong>{' '}
                  {component || 'Not specified'}
                </p>

                <p>
                  <strong>MOS:</strong>{' '}
                  {mos || 'Not specified'}
                </p>
              </div>

              <button
                type="button"
                onClick={clearProfile}
              >
                Clear Active Profile
              </button>
            </>
          )}
        </section>
      )}

      {activeTab === 'tests' && (
        <section className="calculator">
          <h2>AFT Test Record</h2>

          {!userId && (
            <p className="error">
              Please create a Soldier profile first.
            </p>
          )}

          {userId && (
            <>
              <p>
                Active Soldier: {username} | User ID: {userId}
              </p>

              <div className="form-group">
                <label htmlFor="testDate">
                  Test Date
                </label>

                <input
                  id="testDate"
                  type="date"
                  value={testDate}
                  onChange={(event) =>
                    setTestDate(event.target.value)
                  }
                />
              </div>

              <div className="form-group">
                <label htmlFor="testStandardType">
                  Standard Type
                </label>

                <select
                  id="testStandardType"
                  value={testStandardType}
                  onChange={(event) =>
                    setTestStandardType(event.target.value)
                  }
                >
                  <option value="general">
                    General
                  </option>

                  <option value="combat">
                    Combat
                  </option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="deadliftPerformance">
                  Deadlift (lb)
                </label>

                <input
                  id="deadliftPerformance"
                  type="number"
                  value={deadliftPerformance}
                  onChange={(event) =>
                    setDeadliftPerformance(event.target.value)
                  }
                  placeholder="Example: 250"
                />
              </div>

              <div className="form-group">
                <label htmlFor="hrpPerformance">
                  Hand-Release Push-Ups
                </label>

                <input
                  id="hrpPerformance"
                  type="number"
                  value={hrpPerformance}
                  onChange={(event) =>
                    setHrpPerformance(event.target.value)
                  }
                  placeholder="Example: 40"
                />
              </div>

              <div className="form-group">
                <label htmlFor="sdcPerformance">
                  Sprint-Drag-Carry
                </label>

                <input
                  id="sdcPerformance"
                  type="text"
                  value={sdcPerformance}
                  onChange={(event) =>
                    setSdcPerformance(event.target.value)
                  }
                  placeholder="MM:SS, e.g. 1:45"
                />
              </div>

              <div className="form-group">
                <label htmlFor="plankPerformance">
                  Plank
                </label>

                <input
                  id="plankPerformance"
                  type="text"
                  value={plankPerformance}
                  onChange={(event) =>
                    setPlankPerformance(event.target.value)
                  }
                  placeholder="MM:SS, e.g. 2:30"
                />
              </div>

              <div className="form-group">
                <label htmlFor="twoMileRunPerformance">
                  Two-Mile Run
                </label>

                <input
                  id="twoMileRunPerformance"
                  type="text"
                  value={twoMileRunPerformance}
                  onChange={(event) =>
                    setTwoMileRunPerformance(event.target.value)
                  }
                  placeholder="MM:SS, e.g. 16:30"
                />
              </div>

              <button
                type="button"
                onClick={saveAftTest}
                disabled={aftLoading}
              >
                {aftLoading
                  ? 'Saving...'
                  : 'Save AFT Test'}
              </button>

              <button
                type="button"
                onClick={loadAftHistory}
              >
                Refresh History
              </button>

              {aftMessage && (
                <p>
                  {aftMessage}
                </p>
              )}

              <hr />

              <h2>AFT Test History</h2>

              {aftHistory.length === 0 && (
                <p>
                  No AFT tests saved yet.
                </p>
              )}

              {aftHistory.map((test) => (
                <div
                  key={test.id}
                  className="score-result"
                >
                  <h3>
                    {test.test_date}
                  </h3>

                  <p>
                    <strong>Deadlift:</strong>{' '}
                    {test.deadlift.performance} lb
                    {' — '}
                    {test.deadlift.score} pts
                  </p>

                  <p>
                    <strong>HRP:</strong>{' '}
                    {test.hrp.performance} reps
                    {' — '}
                    {test.hrp.score} pts
                  </p>

                  <p>
                    <strong>SDC:</strong>{' '}
                    {test.sdc.performance}
                    {' — '}
                    {test.sdc.score} pts
                  </p>

                  <p>
                    <strong>Plank:</strong>{' '}
                    {test.plank.performance}
                    {' — '}
                    {test.plank.score} pts
                  </p>

                  <p>
                    <strong>2-Mile Run:</strong>{' '}
                    {test.two_mile_run.performance}
                    {' — '}
                    {test.two_mile_run.score} pts
                  </p>

                  <h3>
                    Total: {test.total_score}
                  </h3>
                </div>
              ))}
            </>
          )}
        </section>
      )}

      {activeTab === 'dashboard' && (
  <section className="calculator">
    <h2>AFT Progress Dashboard</h2>

    {!userId && (
      <p className="error">
        Please create a Soldier profile first.
      </p>
    )}

    {userId && aftHistory.length === 0 && (
      <p>
        No AFT test history is available yet.
      </p>
    )}

    {userId && latestTest && (
      <>
        <div className="score-result">
          <h3>Latest AFT Score</h3>

          <p>
            <strong>Test Date:</strong>{' '}
            {latestTest.test_date}
          </p>

          <p>
            <strong>Total Score:</strong>{' '}
            {latestTest.total_score}
          </p>

          {scoreChange !== null && (
            <p>
              <strong>Change:</strong>{' '}
              {scoreChange > 0
                ? `+${scoreChange}`
                : scoreChange}
            </p>
          )}
        </div>

        <div className="score-result">
          <h3>Latest Event Performance</h3>

          <p>
            <strong>Deadlift:</strong>{' '}
            {latestTest.deadlift.performance} lb
            {' — '}
            {latestTest.deadlift.score} pts
          </p>

          <p>
            <strong>HRP:</strong>{' '}
            {latestTest.hrp.performance} reps
            {' — '}
            {latestTest.hrp.score} pts
          </p>

          <p>
            <strong>SDC:</strong>{' '}
            {latestTest.sdc.performance}
            {' — '}
            {latestTest.sdc.score} pts
          </p>

          <p>
            <strong>Plank:</strong>{' '}
            {latestTest.plank.performance}
            {' — '}
            {latestTest.plank.score} pts
          </p>

          <p>
            <strong>2-Mile Run:</strong>{' '}
            {latestTest.two_mile_run.performance}
            {' — '}
            {latestTest.two_mile_run.score} pts
          </p>
        </div>

        <div className="score-result">
          <h3>Score History</h3>

            {aftHistory.map((test) => (
              <p key={test.id}>
                <strong>{test.test_date}:</strong>{' '}
                {test.total_score}
              </p>
            ))}
        </div>

        <div className="score-result">
          <h3>AFT Score Progress</h3>

          {chartData.length < 2 ? (
            <p>
              Save at least two AFT tests to display your progress chart.
            </p>
          ) : (
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis dataKey="date" />

                  <YAxis
                    domain={[0, 500]}
                  />

                  <Tooltip />

                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="#2563eb"
                    strokeWidth={3}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
        </>
      )}
    </section>
  )}
    </main>
  )
}

export default App