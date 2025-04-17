import { Search } from 'lucide-react';

export default function SearchBar() {
  return (
    <div className="relative max-w-4xl mx-auto mt-12">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <Search className="h-5 w-5 text-gray-400" />
      </div>
      <input
        type="text"
        className="block w-full pl-10 pr-3 py-4 text-lg border border-gray-300 rounded-lg 
                 bg-white placeholder-gray-400 focus:outline-none focus:ring-2 
                 focus:ring-emerald-500 focus:border-emerald-500 transition duration-150"
        placeholder="Enter patent number or keywords"
      />
    </div>
  );
}