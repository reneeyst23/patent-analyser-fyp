import SearchBar from "./SearchBar";
import UploadSection from "./UploadSection";

export default function PDFUpload() {
    return (
        <main className="flex-1 p-6 overflow-auto bg-gray-50">
            <div className="text-center">
                <h2 className="text-4xl font-bold text-gray-900">
                Discover Sustainable Innovation
                </h2>
                <p className="mt-6 text-xl text-gray-600 max-w-4xl mx-auto">
                Analyze and explore eco-friendly patents to drive environmental innovation
                </p>
            </div>

            <div className="mt-8 space-y-6">
                <SearchBar />
                <UploadSection />
            </div>
        </main>
    );
}