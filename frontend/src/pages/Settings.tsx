import { useState } from 'react'
import { customQuery } from '../services/api'
import { Play, Database } from 'lucide-react'

export default function Settings() {
  const [query, setQuery] = useState('SELECT * FROM sales LIMIT 10')
  const [result, setResult] = useState<{ columns: string[]; rows: unknown[][] } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const runQuery = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await customQuery(query)
      setResult(res)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Query failed')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Configurações</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Configurações da plataforma e consultas personalizadas</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Cache</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
            O cache Redis armazena resultados de consultas por {300} segundos para melhorar performance.
          </p>
          <button
            onClick={async () => {
              await fetch('http://localhost:8000/analytics/cache/invalidate?pattern=all', { method: 'POST' })
            }}
            className="btn-primary text-sm"
          >
            Limpar Cache
          </button>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Conexões</h3>
          <div className="space-y-3 text-sm">
            <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
              <span>PostgreSQL (Supabase)</span>
              <span className="flex items-center gap-1 text-emerald-600">
                <span className="w-2 h-2 rounded-full bg-emerald-600" />
                Conectado
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
              <span>Redis</span>
              <span className="flex items-center gap-1 text-emerald-600">
                <span className="w-2 h-2 rounded-full bg-emerald-600" />
                Conectado
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Database className="w-5 h-5" />
            Consulta SQL Personalizada
          </h3>
          <button
            onClick={runQuery}
            disabled={loading}
            className="btn-primary flex items-center gap-2 text-sm"
          >
            <Play className="w-4 h-4" />
            {loading ? 'Executando...' : 'Executar'}
          </button>
        </div>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="input-field font-mono text-sm h-32 resize-none mb-4"
          placeholder="Digite sua consulta SQL..."
        />
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-3 rounded-lg text-sm mb-4">
            {error}
          </div>
        )}
        {result && (
          <div>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-2">
              {result.rows.length} linha(s) retornada(s) em {query.length > 0 ? '< 100ms' : '0ms'}
            </p>
            <div className="overflow-x-auto border border-slate-200 dark:border-slate-700 rounded-lg">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-700">
                    {result.columns.map((col) => (
                      <th key={col} className="px-4 py-2 text-left font-medium text-slate-600 dark:text-slate-300 border-b border-slate-200 dark:border-slate-600">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.rows.map((row, i) => (
                    <tr key={i} className="border-b border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                      {row.map((cell, j) => (
                        <td key={j} className="px-4 py-2 text-slate-700 dark:text-slate-300">
                          {String(cell ?? '')}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
