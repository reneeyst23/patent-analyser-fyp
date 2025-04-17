import React from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import UploadSection from './components/UploadSection';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 min-w-[1024px]">
      <Header />
      <main className="max-w-[1400px] mx-auto px-12 py-12">
        <div className="text-center">
          <h2 className="text-4xl font-bold text-gray-900">
            Discover Sustainable Innovation
          </h2>
          <p className="mt-6 text-xl text-gray-600 max-w-4xl mx-auto">
            Analyze and explore eco-friendly patents to drive environmental innovation
          </p>
        </div>
        <SearchBar />
        <UploadSection />
      </main>
    </div>
  );

}
export default App;
