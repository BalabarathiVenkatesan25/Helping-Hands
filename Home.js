import React from "react";

const Home = () => {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <nav className="bg-white shadow-md py-4 px-6 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-green-600">Helping Hands</h1>
        <div className="space-x-6">
          <a href="#about" className="hover:text-green-600 font-medium">
            About
          </a>
          <a href="#how" className="hover:text-green-600 font-medium">
            How It Works
          </a>
          <a href="/login" className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">
            Login
          </a>
          <a href="/register" className="bg-orange-500 text-white px-4 py-2 rounded-md hover:bg-orange-600">
            Register
          </a>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="flex flex-col md:flex-row items-center justify-between bg-green-50 py-16 px-6 md:px-20">
        <div className="md:w-1/2 space-y-6">
          <h2 className="text-4xl md:text-5xl font-bold text-green-700">
            Connecting Donors with Orphanages
          </h2>
          <p className="text-gray-600 text-lg">
            A platform to make donations easy, transparent, and impactful.
            Join us to bring smiles to those who need it the most.
          </p>
          <div className="space-x-4">
            <a
              href="/donate"
              className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700"
            >
              Donate Now
            </a>
            <a
              href="/register"
              className="bg-orange-500 text-white px-6 py-3 rounded-md hover:bg-orange-600"
            >
              Find Support
            </a>
          </div>
        </div>
        {/* <div className="md:w-1/2 mt-10 md:mt-0">
          <img
            src="https://i.ibb.co/7gM6QdM/helping-hands.png"
            alt="Helping Hands"
            className="rounded-lg shadow-lg"
          />
        </div> */}
      </section>

      {/* About Section */}
      <section id="about" className="py-16 px-6 md:px-20 bg-white">
        <h3 className="text-3xl font-bold text-center text-green-700 mb-12">
          Our Mission
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {[
            { title: "Food", icon: "🍚", desc: "Providing nutritious meals to orphanages." },
            { title: "Funds", icon: "💰", desc: "Helping with essential financial support." },
            { title: "Education", icon: "📚", desc: "Empowering children through learning." },
            { title: "Clothes", icon: "👕", desc: "Supplying clothing for all seasons." },
          ].map((item, idx) => (
            <div
              key={idx}
              className="bg-green-50 p-6 rounded-lg shadow hover:shadow-lg transition"
            >
              <div className="text-5xl">{item.icon}</div>
              <h4 className="mt-4 text-xl font-semibold text-green-700">{item.title}</h4>
              <p className="text-gray-600 mt-2">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section id="how" className="py-16 px-6 md:px-20 bg-green-50">
        <h3 className="text-3xl font-bold text-center text-green-700 mb-12">
          How It Works
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
          {[
            { step: "1", title: "Register", desc: "Sign up as a donor or orphanage." },
            { step: "2", title: "Connect", desc: "Browse needs or post requests." },
            { step: "3", title: "Donate", desc: "Make contributions easily." },
            { step: "4", title: "Impact", desc: "See the positive change you made." },
          ].map((item, idx) => (
            <div
              key={idx}
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition"
            >
              <div className="text-green-600 text-4xl font-bold">{item.step}</div>
              <h4 className="mt-4 text-xl font-semibold text-green-700">{item.title}</h4>
              <p className="text-gray-600 mt-2">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-green-700 text-white text-center py-6 mt-auto">
        <p>© {new Date().getFullYear()} Helping Hands. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Home;
