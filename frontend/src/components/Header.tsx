import { Leaf } from 'lucide-react';

export default function Header() {
  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-[1400px] mx-auto px-12 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Leaf className="h-10 w-10 text-emerald-600" />
            <h1 className="ml-3 text-3xl font-bold text-gray-900">EcoPatent Analyzer</h1>
          </div>
          <nav className="flex space-x-12">
            {/* <a href="#" className="text-gray-600 hover:text-emerald-600">Dashboard</a>
            <a href="#" className="text-gray-600 hover:text-emerald-600">Analysis</a>
            <a href="#" className="text-gray-600 hover:text-emerald-600">About</a> */}
          </nav>
        </div>
      </div>
    </header>
  );
}