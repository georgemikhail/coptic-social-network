import { useState, useEffect } from 'react';
import Link from 'next/link';
import Head from 'next/head';

export default function HomePage() {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 100);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
      <Head>
        <title>Coptic Social Network - Connect with the Global Coptic Community</title>
        <meta name="description" content="Join thousands of Coptic Orthodox Christians worldwide. Share your faith journey, connect with your parish, and strengthen your spiritual community." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link 
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@400;600;700&display=swap" 
          rel="stylesheet" 
        />
      </Head>

      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 py-16">
          <div className="text-center">
            <h1 className="text-6xl font-bold text-gray-900 mb-8">
              ⛪ Coptic Social Network
            </h1>
            <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
              Connect with Coptic Orthodox Christians worldwide. Share your faith journey, 
              connect with your parish, and strengthen your spiritual community.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <a 
                href="/auth/register"
                className="inline-flex items-center justify-center rounded-lg text-lg font-medium bg-blue-600 text-white hover:bg-blue-700 px-8 py-3 shadow-lg transition-colors"
              >
                🙏 Join Our Community
              </a>
              <a 
                href="/auth/login"
                className="inline-flex items-center justify-center rounded-lg text-lg font-medium border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white px-8 py-3 transition-colors"
              >
                Sign In
              </a>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="bg-white rounded-xl p-8 shadow-lg">
                <div className="text-4xl mb-4">👥</div>
                <h3 className="text-xl font-semibold mb-2">Community Groups</h3>
                <p className="text-gray-600">
                  Join ministries, Bible study groups, and prayer circles.
                </p>
              </div>
              
              <div className="bg-white rounded-xl p-8 shadow-lg">
                <div className="text-4xl mb-4">📱</div>
                <h3 className="text-xl font-semibold mb-2">Social Feed</h3>
                <p className="text-gray-600">
                  Share spiritual insights and prayer requests with your community.
                </p>
              </div>
              
              <div className="bg-white rounded-xl p-8 shadow-lg">
                <div className="text-4xl mb-4">⛪</div>
                <h3 className="text-xl font-semibold mb-2">Parish Connection</h3>
                <p className="text-gray-600">
                  Connect with your local parish and community events.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
} 