import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import NFTPackForm from './NFTPackForm';

interface AddNFTPackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
}

const AddNFTPackModal: React.FC<AddNFTPackModalProps> = ({ isOpen, onClose, onSubmit }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-gray-800 p-4 rounded-lg shadow-lg max-w-md w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            
            <NFTPackForm onSubmit={(data) => {
              onSubmit(data);
              onClose();
            }} />
            <button
              onClick={onClose}
              className="mt-3 w-full bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-all duration-300 text-sm"
            >
              Cancel
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default AddNFTPackModal;