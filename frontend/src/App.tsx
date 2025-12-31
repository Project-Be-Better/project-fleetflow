import { useState } from "react";

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-8">
      <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full text-center">
        <h1 className="text-4xl font-black text-blue-600 mb-4">FleetFlow</h1>
        <p className="text-gray-600 mb-8">
          Tailwind CSS v4 + React + TypeScript
        </p>

        <div className="space-y-4">
          <button
            onClick={() => setCount((count) => count + 1)}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors duration-200 shadow-lg hover:shadow-blue-200"
          >
            Count is {count}
          </button>

          <p className="text-sm text-gray-400">
            Edit{" "}
            <code className="bg-gray-100 px-1 rounded text-blue-500">
              src/App.tsx
            </code>{" "}
            to test HMR
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
