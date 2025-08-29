export default function Home() {
  return (
    <div className="font-sans grid grid-rows-[auto_1fr_auto] items-center justify-items-center min-h-screen p-8 pb-20 sm:pt-0 gap-16 sm:p-20">
      <header className="w-full bg-gray-800 text-white p-4 text-center fixed top-0 left-0">
        Pythula code review
      </header>
      <main className="flex flex-col gap-4 row-start-2 items-center sm:items-start w-full">
        <textarea
          className="flex basis-1/2 h-64 p-4 border border-gray-300 rounded-md font-mono resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Paste your code snippet here..."
        ></textarea>
        <button className="flex px-4 py-2 bg-blue-500 text-white rounded-sm hover:bg-blue-600">
          Submit
        </button>
      </main>
      <footer className="w-full bg-gray-800 p-2 text-white text-center size-sm absolute bottom-0 min-h-10">
      </footer>
    </div>
  );
}
