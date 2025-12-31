import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-8">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-xl">
        <h1 className="mb-4 text-4xl font-black text-blue-600">FleetFlow</h1>
        <p className="mb-8 px-2 text-red-600">Tailwind CSS v4 + React + TypeScript</p>

        <div className="space-y-4">
          <button
            onClick={() => setCount((count) => count + 1)}
            className="w-full rounded-lg bg-blue-600 px-6 py-3 font-bold text-white shadow-lg transition-colors duration-200 hover:bg-blue-700 hover:shadow-blue-200"
          >
            Count is {count}
          </button>

          <p className="text-sm text-gray-400">
            Edit <code className="rounded bg-gray-100 px-1 text-blue-500">src/App.tsx</code> to test
            HMR
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
