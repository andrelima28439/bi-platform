import { Download } from 'lucide-react'
import { getExportUrl } from '../services/api'

interface ExportButtonProps {
  reportType: string
  filter?: { start_date?: string; end_date?: string; period?: string }
}

export default function ExportButton({ reportType, filter }: ExportButtonProps) {
  return (
    <div className="flex gap-2">
      <a
        href={getExportUrl(reportType, 'csv', filter)}
        className="btn-secondary flex items-center gap-2 text-sm"
        download
      >
        <Download className="w-4 h-4" />
        CSV
      </a>
      <a
        href={getExportUrl(reportType, 'pdf', filter)}
        className="btn-secondary flex items-center gap-2 text-sm"
        download
      >
        <Download className="w-4 h-4" />
        PDF
      </a>
    </div>
  )
}
