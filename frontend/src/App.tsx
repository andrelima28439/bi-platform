import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import SalesReport from './pages/SalesReport'
import CustomersReport from './pages/CustomersReport'
import ProductsReport from './pages/ProductsReport'
import TrendsAnalysis from './pages/TrendsAnalysis'
import Settings from './pages/Settings'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/vendas" element={<SalesReport />} />
          <Route path="/clientes" element={<CustomersReport />} />
          <Route path="/produtos" element={<ProductsReport />} />
          <Route path="/tendencias" element={<TrendsAnalysis />} />
          <Route path="/configuracoes" element={<Settings />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
