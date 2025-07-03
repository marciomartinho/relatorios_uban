import os
import pickle
import hashlib
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class CacheService:
    """Serviço de cache para otimizar carregamento de dados"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(hours=2)  # Cache válido por 2 horas
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Garante que o diretório de cache existe"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_file_hash(self, file_path: str) -> str:
        """Calcula hash do arquivo para detectar mudanças"""
        if not os.path.exists(file_path):
            return ""
        
        # Usa timestamp de modificação + tamanho para hash rápido
        stat = os.stat(file_path)
        hash_string = f"{stat.st_mtime}_{stat.st_size}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Gera caminho do arquivo de cache"""
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Verifica se o cache ainda é válido"""
        if not os.path.exists(cache_path):
            return False
        
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        return datetime.now() - cache_time < self.cache_duration
    
    def get_cached_dataframe(self, file_path: str, cache_key: str) -> Optional[pd.DataFrame]:
        """Recupera DataFrame do cache se válido"""
        file_hash = self._get_file_hash(file_path)
        full_cache_key = f"{cache_key}_{file_hash}"
        cache_path = self._get_cache_path(full_cache_key)
        
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                    print(f"✅ Cache HIT para {cache_key}")
                    return cached_data
            except Exception as e:
                print(f"⚠️ Erro ao carregar cache: {e}")
                # Remove cache corrompido
                if os.path.exists(cache_path):
                    os.remove(cache_path)
        
        return None
    
    def cache_dataframe(self, df: pd.DataFrame, file_path: str, cache_key: str):
        """Armazena DataFrame no cache"""
        file_hash = self._get_file_hash(file_path)
        full_cache_key = f"{cache_key}_{file_hash}"
        cache_path = self._get_cache_path(full_cache_key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(df, f)
            print(f"💾 DataFrame cacheado para {cache_key}")
        except Exception as e:
            print(f"⚠️ Erro ao salvar cache: {e}")
    
    def clear_cache(self):
        """Limpa todo o cache"""
        if os.path.exists(self.cache_dir):
            for file in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, file)
                try:
                    os.remove(file_path)
                    print(f"🗑️ Cache removido: {file}")
                except Exception as e:
                    print(f"⚠️ Erro ao remover cache: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o cache"""
        if not os.path.exists(self.cache_dir):
            return {"total_files": 0, "total_size": 0}
        
        total_files = 0
        total_size = 0
        
        for file in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, file)
            if os.path.isfile(file_path):
                total_files += 1
                total_size += os.path.getsize(file_path)
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }

# Instância global do cache
cache_service = CacheService()