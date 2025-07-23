import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Upload, X, Calendar, Hash, Wand2 } from 'lucide-react';
import type { ManualPostForm as ManualPostFormType } from '../types';

interface ManualPostFormProps {
  onSubmit: (data: ManualPostFormType) => void;
}

const ManualPostForm: React.FC<ManualPostFormProps> = ({ onSubmit }) => {
  const { register, handleSubmit, formState: { errors }, watch, setValue } = useForm<ManualPostFormType>({
    defaultValues: {
      text: '',
      images: [],
      genre: '',
      scheduledTime: '',
      aiMode: false
    }
  });
  
  const [previewImages, setPreviewImages] = useState<string[]>([]);
  const [imageFiles, setImageFiles] = useState<File[]>([]);
  const aiMode = watch('aiMode');
  const textLength = watch('text')?.length || 0;

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length + imageFiles.length > 4) {
      alert('最大4枚まで画像をアップロードできます');
      return;
    }

    const validFiles = files.filter(file => {
      const isValid = ['image/jpeg', 'image/png', 'image/gif'].includes(file.type);
      const isUnder5MB = file.size <= 5 * 1024 * 1024;
      return isValid && isUnder5MB;
    });

    if (validFiles.length !== files.length) {
      alert('JPG、PNG、GIF形式で5MB以内の画像をアップロードしてください');
    }

    const newImageFiles = [...imageFiles, ...validFiles];
    setImageFiles(newImageFiles);
    setValue('images', newImageFiles);

    const newPreviews = validFiles.map(file => URL.createObjectURL(file));
    setPreviewImages([...previewImages, ...newPreviews]);
  };

  const removeImage = (index: number) => {
    const newImageFiles = imageFiles.filter((_, i) => i !== index);
    const newPreviews = previewImages.filter((_, i) => i !== index);
    setImageFiles(newImageFiles);
    setPreviewImages(newPreviews);
    setValue('images', newImageFiles);
  };

  const onFormSubmit = (data: ManualPostFormType) => {
    const submitData = {
      ...data,
      images: imageFiles
    };
    onSubmit(submitData);
  };

  const getMinDateTime = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 30);
    return now.toISOString().slice(0, 16);
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6 bg-white p-6 rounded-lg shadow-md">
      <div>
        <label htmlFor="text" className="block text-sm font-medium text-gray-700 mb-2">
          投稿テキスト <span className="text-red-500">*</span>
        </label>
        <textarea
          id="text"
          {...register('text', { 
            required: '投稿テキストは必須です',
            maxLength: {
              value: 500,
              message: '投稿テキストは500文字以内で入力してください'
            }
          })}
          className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={6}
          placeholder="投稿内容を入力してください..."
        />
        <div className="mt-1 flex justify-between">
          <span className="text-sm text-gray-500">{textLength} / 500文字</span>
          {errors.text && <span className="text-sm text-red-500">{errors.text.message}</span>}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          画像アップロード（最大4枚）
        </label>
        <div className="space-y-4">
          <div className="flex items-center justify-center w-full">
            <label htmlFor="images" className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <Upload className="w-8 h-8 mb-2 text-gray-400" />
                <p className="mb-2 text-sm text-gray-500">
                  <span className="font-semibold">クリックしてアップロード</span>
                </p>
                <p className="text-xs text-gray-500">JPG, PNG, GIF (最大5MB)</p>
              </div>
              <input
                id="images"
                type="file"
                multiple
                accept="image/jpeg,image/png,image/gif"
                className="hidden"
                onChange={handleImageChange}
              />
            </label>
          </div>
          
          {previewImages.length > 0 && (
            <div className="grid grid-cols-2 gap-4">
              {previewImages.map((preview, index) => (
                <div key={index} className="relative">
                  <img src={preview} alt={`Preview ${index + 1}`} className="w-full h-32 object-cover rounded-lg" />
                  <button
                    type="button"
                    onClick={() => removeImage(index)}
                    className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div>
        <label htmlFor="genre" className="block text-sm font-medium text-gray-700 mb-2">
          <Hash className="inline w-4 h-4 mr-1" />
          投稿ジャンル <span className="text-red-500">*</span>
        </label>
        <input
          id="genre"
          type="text"
          {...register('genre', { required: '投稿ジャンルは必須です' })}
          className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="例: AI活用術、副業情報など"
        />
        {errors.genre && <span className="text-sm text-red-500">{errors.genre.message}</span>}
      </div>

      <div>
        <label htmlFor="scheduledTime" className="block text-sm font-medium text-gray-700 mb-2">
          <Calendar className="inline w-4 h-4 mr-1" />
          投稿希望日時 <span className="text-red-500">*</span>
        </label>
        <input
          id="scheduledTime"
          type="datetime-local"
          {...register('scheduledTime', { 
            required: '投稿希望日時は必須です',
            validate: (value) => {
              const selectedTime = new Date(value);
              const minTime = new Date();
              minTime.setMinutes(minTime.getMinutes() + 30);
              return selectedTime >= minTime || '投稿希望日時は現在時刻から30分以降を選択してください';
            }
          })}
          min={getMinDateTime()}
          className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        {errors.scheduledTime && <span className="text-sm text-red-500">{errors.scheduledTime.message}</span>}
      </div>

      <div className="flex items-center">
        <input
          id="aiMode"
          type="checkbox"
          {...register('aiMode')}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="aiMode" className="ml-2 block text-sm text-gray-900">
          <Wand2 className="inline w-4 h-4 mr-1" />
          AI生成モード（人気投稿を参考に文章を改善）
        </label>
      </div>

      {aiMode && (
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
          <p className="text-sm text-blue-700">
            AI生成モードがONです。入力されたテキストをベースに、人気投稿を参考にして改善案を生成します。
          </p>
        </div>
      )}

      <button
        type="submit"
        className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-200"
      >
        投稿を予約
      </button>
    </form>
  );
};

export default ManualPostForm;