export default function Footer() {
  return (
    <footer className="bg-dark-900 text-white py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* About */}
          <div>
            <h3 className="text-lg font-bold mb-4">SITARA</h3>
            <p className="text-gray-400 text-sm">
              An Agentic Situational Risk Intelligence Platform for Women's Safety in India
            </p>
          </div>
          
          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-bold mb-4">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Home</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">About</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">How It Works</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy Policy</a></li>
            </ul>
          </div>
          
          {/* Technology */}
          <div>
            <h3 className="text-lg font-bold mb-4">Technology</h3>
            <ul className="space-y-2 text-sm">
              <li className="text-gray-400">Random Forest ML</li>
              <li className="text-gray-400">Agentic FSM</li>
              <li className="text-gray-400">OpenStreetMap</li>
              <li className="text-gray-400">Next.js 14</li>
            </ul>
          </div>
          
          {/* Contact */}
          <div>
            <h3 className="text-lg font-bold mb-4">Data Sources</h3>
            <ul className="space-y-2 text-sm">
              <li className="text-gray-400">Indian Crime Datasets</li>
              <li className="text-gray-400">OpenStreetMap</li>
              <li className="text-gray-400">NCRB Statistics</li>
              <li className="text-gray-400">Open Government Data</li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-800 pt-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <p className="text-gray-400 text-sm mb-4 md:mb-0">
              © 2026 SITARA. Built for women's safety in India 🇮🇳
            </p>
            <div className="flex items-center space-x-6 text-sm text-gray-400">
              <span>Privacy First</span>
              <span>•</span>
              <span>Ethical AI</span>
              <span>•</span>
              <span>Open Source</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
