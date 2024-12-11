"use client";
import { useState } from 'react';
import Image from 'next/image';
import logoImg from '../assets/images/Telegage_logo.png';
import MenuIcon from '../assets/icons/menu.svg';
import Link from 'next/link';

export const Navbar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <div className='bg-black text-white'>
      <div className="container">
        <div className='py-4 flex items-center justify-between'>
          <div className='relative'>
            <div className='absolute w-full top-0 bottom-0 blur-md'></div>
            <Image src={logoImg} alt="saas logo" className='w-20 h-20 relative' />
          </div>
          <div 
            className='border border-white border-opacity-25 h-10 w-10 rounded-lg inline-flex items-center justify-center sm:hidden cursor-pointer'
            onClick={toggleMobileMenu}
          >
            <MenuIcon />
          </div>
          <nav className='items-center gap-6 hidden sm:flex'>
            <Link href='/' className='text-white text-opacity-60 hover:text-opacity-100 transition'>Features</Link>
            <Link href='/' className='text-white text-opacity-60 hover:text-opacity-100 transition'>How It Works</Link>
            <Link href='/' className='text-white text-opacity-60 hover:text-opacity-100 transition'>Pricing</Link>
            
            <Link href='/auth'>
              <button className='bg-white text-black py-2 px-4 rounded-lg hover:scale-[1.03] transition'>
                Get TeleGage
              </button>
            </Link>
          </nav>
        </div>
        
        {/* Mobile menu */}
        {isMobileMenuOpen && (
          <div className='sm:hidden'>
            <nav className='flex flex-col items-center gap-4 py-4'>
              <Link href='/' className='text-white text-opacity-60 hover:text-opacity-100 transition'>Features</Link>
              <Link href='/' className='text-white text-opacity-60 hover:text-opacity-100 transition'>How It Works</Link>
              <Link href='/' className='text-white text-opacity-60 hover:text-opacity-100 transition'>Pricing</Link>
              <Link href='/auth'>
                <button className='bg-white text-black py-2 px-4 rounded-lg hover:scale-[1.03] transition'>
                  Get TeleGage
                </button>
              </Link>
            </nav>
          </div>
        )}
      </div>
    </div>
  );
};
