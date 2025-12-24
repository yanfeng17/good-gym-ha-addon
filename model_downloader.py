"""
Model downloader for Good-GYM Home Assistant Addon
Automatically downloads RTMPose models on first run
"""
import os
import sys
import urllib.request
from pathlib import Path


class ModelDownloader:
    """Download RTMPose models if not present"""
    
    def __init__(self, models_dir="models"):
        """
        Initialize model downloader
        
        Args:
            models_dir: Directory to store model files
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Model URLs (from OpenMMLab)
        self.models = {
            'rtmpose-m_8xb64-270e_coco-wholebody-256x192-cd5e845c_20221122.onnx': 
                'https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/rtmpose-m_8xb64-270e_coco-wholebody-256x192-cd5e845c_20221122.onnx',
            'rtmdet-nano_8xb32-300e_coco-obj365-person-05d8511e.onnx':
                'https://download.openmmlab.com/mmpose/v1/projects/rtmposev1/onnx_sdk/rtmdet-nano_8xb32-300e_coco-obj365-person-05d8511e.onnx',
        }
    
    def download_file(self, url, dest_path):
        """
        Download a file with progress indicator
        
        Args:
            url: URL to download from
            dest_path: Destination file path
        """
        print(f"📥 Downloading: {dest_path.name}")
        print(f"   From: {url}")
        
        def report_progress(block_num, block_size, total_size):
            """Report download progress"""
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            
            # Print progress bar
            bar_length = 50
            filled = int(bar_length * percent / 100)
            bar = '=' * filled + '-' * (bar_length - filled)
            
            # Print on same line
            sys.stdout.write(f'\r   [{bar}] {percent:.1f}%')
            sys.stdout.flush()
        
        try:
            urllib.request.urlretrieve(url, dest_path, reporthook=report_progress)
            print()  # New line after progress bar
            print(f"   ✓ Downloaded successfully\n")
            return True
        except Exception as e:
            print(f"\n   ✗ Download failed: {e}\n")
            return False
    
    def check_and_download(self):
        """
        Check for missing models and download them
        
        Returns:
            True if all models are available, False otherwise
        """
        print("\n" + "="*60)
        print("  RTMPose Model Checker")
        print("="*60 + "\n")
        
        missing_models = []
        
        # Check which models are missing
        for model_name in self.models.keys():
            model_path = self.models_dir / model_name
            if model_path.exists():
                print(f"✓ {model_name} - Already exists")
            else:
                print(f"✗ {model_name} - Missing")
                missing_models.append(model_name)
        
        if not missing_models:
            print("\n✅ All models are present!\n")
            return True
        
        # Download missing models
        print(f"\n📦 Need to download {len(missing_models)} model(s)...\n")
        
        success_count = 0
        for model_name in missing_models:
            model_url = self.models[model_name]
            model_path = self.models_dir / model_name
            
            if self.download_file(model_url, model_path):
                success_count += 1
        
        print("="*60)
        if success_count == len(missing_models):
            print(f"✅ Successfully downloaded all {success_count} model(s)!")
        else:
            print(f"⚠️  Downloaded {success_count}/{len(missing_models)} model(s)")
            print("   Some downloads failed. Please check your internet connection.")
        print("="*60 + "\n")
        
        return success_count == len(missing_models)


def ensure_models_available(models_dir="models"):
    """
    Ensure all required models are available
    
    Args:
        models_dir: Directory where models should be stored
        
    Returns:
        True if all models available, False otherwise
    """
    downloader = ModelDownloader(models_dir)
    return downloader.check_and_download()


if __name__ == "__main__":
    # Test the downloader
    import sys
    
    models_dir = sys.argv[1] if len(sys.argv) > 1 else "models"
    
    print("Testing model downloader...")
    success = ensure_models_available(models_dir)
    
    sys.exit(0 if success else 1)
