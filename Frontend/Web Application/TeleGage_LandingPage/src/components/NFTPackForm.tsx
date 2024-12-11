import { useState } from 'react'
import { motion } from 'framer-motion'
import { Upload } from 'lucide-react'

interface NFTPackData {
  title: string
  price: string
  negative: string
  keywords: string
  altText: string
  imageUrl: string
}

interface NFTPackFormProps {
  onSubmit: (data: NFTPackData) => void
}

export default function NFTPackForm({ onSubmit }: NFTPackFormProps) {
  const [formData, setFormData] = useState<NFTPackData>({
    title: '',
    price: '',
    negative: '',
    keywords: '',
    altText: '',
    imageUrl: '',
  })
  const [imageFile, setImageFile] = useState<File | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImageFile(e.target.files[0])
      setFormData({ ...formData, imageUrl: URL.createObjectURL(e.target.files[0]) })
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!imageFile) {
      alert('Please select an image');
      return;
    }

    const imageData = await new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.readAsDataURL(imageFile);
    });

    const response = await fetch('/api/upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ imageData }),
    });

    if (response.ok) {
      const { imageUrl } = await response.json();
      const nftPackData = {
        ...formData,
        imageUrl,
      };
      console.log("NFTPackForm - Data to be submitted:", nftPackData);
      onSubmit(nftPackData);
    } else {
      alert('Failed to upload image');
    }
  }

  return (
    <div className="space-y-4">
      <motion.form
        onSubmit={handleSubmit}
        className="space-y-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-300 mb-1">
              Title
            </label>
            <input
              type="text"
              name="title"
              id="title"
              value={formData.title}
              onChange={handleChange}
              required
              className="w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 p-2 text-sm transition-all duration-300"
            />
          </div>
          <div>
            <label htmlFor="price" className="block text-sm font-medium text-gray-300 mb-1">
              Price
            </label>
            <input
              type="number"
              name="price"
              id="price"
              value={formData.price}
              onChange={handleChange}
              required
              className="w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 p-2 text-sm transition-all duration-300"
            />
          </div>
        </div>
        <div>
          <label htmlFor="negative" className="block text-sm font-medium text-gray-300 mb-1">
            Negative Keywords
          </label>
          <textarea
            name="negative"
            id="negative"
            value={formData.negative}
            onChange={handleChange}
            required
            className="w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 p-2 text-sm transition-all duration-300"
          />
        </div>
        <div>
          <label htmlFor="keywords" className="block text-sm font-medium text-gray-300 mb-1">
            Keywords
          </label>
          <textarea
            name="keywords"
            id="keywords"
            value={formData.keywords}
            onChange={handleChange}
            required
            className="w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 p-2 text-sm transition-all duration-300"
          />
        </div>
        <div>
          <label htmlFor="altText" className="block text-sm font-medium text-gray-300 mb-1">
            Alt Text
          </label>
          <input
            type="text"
            name="altText"
            id="altText"
            value={formData.altText}
            onChange={handleChange}
            required
            className="w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 p-2 text-sm transition-all duration-300"
          />
        </div>
        <div>
          <label htmlFor="image" className="block text-sm font-medium text-gray-300 mb-1">
            Image
          </label>
          <input
            type="file"
            name="image"
            id="image"
            onChange={handleImageChange}
            required
            className="hidden"
          />
          <label
            htmlFor="image"
            className="cursor-pointer flex items-center justify-center w-full h-32 rounded-md bg-gray-700 border-2 border-dashed border-gray-600 hover:border-indigo-500 transition-colors duration-300"
          >
            {formData.imageUrl ? (
              <img src={formData.imageUrl} alt="Preview" className="max-h-full rounded-md" />
            ) : (
              <div className="text-center">
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <span className="mt-2 block text-sm font-medium text-gray-400">Choose an image</span>
              </div>
            )}
          </label>
        </div>
        <motion.button
          type="submit"
          className="w-full bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white py-2 px-4 rounded-lg hover:opacity-90 transition-all duration-300 flex items-center justify-center"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Upload className="mr-2" />
          Create NFT Pack
        </motion.button>
      </motion.form>
    </div>
  )
}