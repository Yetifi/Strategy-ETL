"""
Prompt storage manager for the Strategy ETL system.
"""
import json
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from .models import UserPrompt, TransformedPrompt, ETLResult


class PromptStorageManager:
    """
    Manages persistent storage of user prompts and ETL results.
    Supports multiple storage backends (SQLite, JSON files).
    """
    
    def __init__(self, storage_type: str = "sqlite", storage_path: Optional[str] = None):
        """
        Initialize the storage manager.
        
        Args:
            storage_type: Type of storage ('sqlite', 'json', 'memory')
            storage_path: Path for storage files
        """
        self.storage_type = storage_type
        self.storage_path = storage_path or self._get_default_storage_path()
        self._initialize_storage()
    
    def _get_default_storage_path(self) -> str:
        """Get default storage path based on storage type."""
        if self.storage_type == "sqlite":
            return "prompts.db"
        elif self.storage_type == "json":
            return "prompts"
        else:
            return "."
    
    def _initialize_storage(self):
        """Initialize the storage backend."""
        if self.storage_type == "sqlite":
            self._init_sqlite()
        elif self.storage_type == "json":
            self._init_json_storage()
    
    def _init_sqlite(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_prompts (
                id TEXT PRIMARY KEY,
                raw_text TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transformed_prompts (
                id TEXT PRIMARY KEY,
                original_prompt_id TEXT NOT NULL,
                strategy_type TEXT NOT NULL,
                primary_asset TEXT,
                secondary_assets TEXT,
                risk_level TEXT NOT NULL,
                target_apy REAL,
                duration_days INTEGER,
                execution_priority TEXT NOT NULL,
                auto_compound BOOLEAN NOT NULL,
                confidence_score REAL NOT NULL,
                transformation_notes TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (original_prompt_id) REFERENCES user_prompts (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS etl_results (
                id TEXT PRIMARY KEY,
                original_prompt_id TEXT NOT NULL,
                transformed_prompt_id TEXT,
                success BOOLEAN NOT NULL,
                errors TEXT,
                warnings TEXT,
                processing_time_ms REAL NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (original_prompt_id) REFERENCES user_prompts (id),
                FOREIGN KEY (transformed_prompt_id) REFERENCES transformed_prompts (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _init_json_storage(self):
        """Initialize JSON file storage."""
        Path(self.storage_path).mkdir(exist_ok=True)
        
        # Create index files if they don't exist
        index_file = Path(self.storage_path) / "index.json"
        if not index_file.exists():
            with open(index_file, 'w') as f:
                json.dump({
                    "user_prompts": [],
                    "transformed_prompts": [],
                    "etl_results": []
                }, f, indent=2)
    
    def store_user_prompt(self, prompt: UserPrompt) -> bool:
        """Store a user prompt."""
        try:
            if self.storage_type == "sqlite":
                return self._store_user_prompt_sqlite(prompt)
            elif self.storage_type == "json":
                return self._store_user_prompt_json(prompt)
            else:
                return False
        except Exception as e:
            print(f"Error storing user prompt: {e}")
            return False
    
    def _store_user_prompt_sqlite(self, prompt: UserPrompt) -> bool:
        """Store user prompt in SQLite."""
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_prompts 
            (id, raw_text, timestamp, user_id, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            prompt.id,
            prompt.raw_text,
            prompt.timestamp.isoformat(),
            prompt.user_id,
            json.dumps(prompt.metadata)
        ))
        
        conn.commit()
        conn.close()
        return True
    
    def _store_user_prompt_json(self, prompt: UserPrompt) -> bool:
        """Store user prompt as JSON file."""
        prompt_file = Path(self.storage_path) / f"prompt_{prompt.id}.json"
        
        prompt_data = {
            "id": prompt.id,
            "raw_text": prompt.raw_text,
            "timestamp": prompt.timestamp.isoformat(),
            "user_id": prompt.user_id,
            "metadata": prompt.metadata
        }
        
        with open(prompt_file, 'w') as f:
            json.dump(prompt_data, f, indent=2)
        
        # Update index
        self._update_json_index("user_prompts", prompt.id, prompt_file.name)
        return True
    
    def store_transformed_prompt(self, prompt: TransformedPrompt) -> bool:
        """Store a transformed prompt."""
        try:
            if self.storage_type == "sqlite":
                return self._store_transformed_prompt_sqlite(prompt)
            elif self.storage_type == "json":
                return self._store_transformed_prompt_json(prompt)
            else:
                return False
        except Exception as e:
            print(f"Error storing transformed prompt: {e}")
            return False
    
    def _store_transformed_prompt_sqlite(self, prompt: TransformedPrompt) -> bool:
        """Store transformed prompt in SQLite."""
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO transformed_prompts 
            (id, original_prompt_id, strategy_type, primary_asset, secondary_assets,
             risk_level, target_apy, duration_days, execution_priority, 
             auto_compound, confidence_score, transformation_notes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prompt.id,
            prompt.original_prompt_id,
            prompt.strategy_type.value,
            prompt.primary_asset.value if prompt.primary_asset else None,
            json.dumps([asset.value for asset in prompt.secondary_assets]),
            prompt.risk_level.value,
            prompt.target_apy,
            prompt.duration_days,
            prompt.execution_priority,
            prompt.auto_compound,
            prompt.confidence_score,
            json.dumps(prompt.transformation_notes),
            prompt.timestamp.isoformat()
        ))
        
        conn.commit()
        conn.close()
        return True
    
    def _store_transformed_prompt_json(self, prompt: TransformedPrompt) -> bool:
        """Store transformed prompt as JSON file."""
        prompt_file = Path(self.storage_path) / f"transformed_{prompt.id}.json"
        
        prompt_data = {
            "id": prompt.id,
            "original_prompt_id": prompt.original_prompt_id,
            "strategy_type": prompt.strategy_type.value,
            "primary_asset": prompt.primary_asset.value if prompt.primary_asset else None,
            "secondary_assets": [asset.value for asset in prompt.secondary_assets],
            "risk_level": prompt.risk_level.value,
            "target_apy": prompt.target_apy,
            "duration_days": prompt.duration_days,
            "execution_priority": prompt.execution_priority,
            "auto_compound": prompt.auto_compound,
            "confidence_score": prompt.confidence_score,
            "transformation_notes": prompt.transformation_notes,
            "timestamp": prompt.timestamp.isoformat()
        }
        
        with open(prompt_file, 'w') as f:
            json.dump(prompt_data, f, indent=2)
        
        # Update index
        self._update_json_index("transformed_prompts", prompt.id, prompt_file.name)
        return True
    
    def store_etl_result(self, result: ETLResult) -> bool:
        """Store an ETL result."""
        try:
            if self.storage_type == "sqlite":
                return self._store_etl_result_sqlite(result)
            elif self.storage_type == "json":
                return self._store_etl_result_json(result)
            else:
                return False
        except Exception as e:
            print(f"Error storing ETL result: {e}")
            return False
    
    def _store_etl_result_sqlite(self, result: ETLResult) -> bool:
        """Store ETL result in SQLite."""
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO etl_results 
            (id, original_prompt_id, transformed_prompt_id, success, errors, 
             warnings, processing_time_ms, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(hash(result.original_prompt.id + str(result.original_prompt.timestamp))),
            result.original_prompt.id,
            result.transformed_prompt.id if result.transformed_prompt else None,
            result.success,
            json.dumps(result.errors),
            json.dumps(result.warnings),
            result.processing_time_ms,
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return True
    
    def _store_etl_result_json(self, result: ETLResult) -> bool:
        """Store ETL result as JSON file."""
        result_file = Path(self.storage_path) / f"result_{hash(result.original_prompt.id + str(result.original_prompt.timestamp))}.json"
        
        result_data = {
            "id": str(hash(result.original_prompt.id + str(result.original_prompt.timestamp))),
            "original_prompt_id": result.original_prompt.id,
            "transformed_prompt_id": result.transformed_prompt.id if result.transformed_prompt else None,
            "success": result.success,
            "errors": result.errors,
            "warnings": result.warnings,
            "processing_time_ms": result.processing_time_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        # Update index
        self._update_json_index("etl_results", result_data["id"], result_file.name)
        return True
    
    def _update_json_index(self, collection: str, item_id: str, filename: str):
        """Update the JSON index file."""
        index_file = Path(self.storage_path) / "index.json"
        
        with open(index_file, 'r') as f:
            index = json.load(f)
        
        # Add or update item in index
        item_entry = {"id": item_id, "filename": filename}
        
        # Remove existing entry if it exists
        index[collection] = [item for item in index[collection] if item["id"] != item_id]
        
        # Add new entry
        index[collection].append(item_entry)
        
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def get_user_prompts(self, limit: Optional[int] = None, user_id: Optional[str] = None) -> List[UserPrompt]:
        """Retrieve user prompts."""
        try:
            if self.storage_type == "sqlite":
                return self._get_user_prompts_sqlite(limit, user_id)
            elif self.storage_type == "json":
                return self._get_user_prompts_json(limit, user_id)
            else:
                return []
        except Exception as e:
            print(f"Error retrieving user prompts: {e}")
            return []
    
    def _get_user_prompts_sqlite(self, limit: Optional[int] = None, user_id: Optional[str] = None) -> List[UserPrompt]:
        """Retrieve user prompts from SQLite."""
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()
        
        query = "SELECT id, raw_text, timestamp, user_id, metadata FROM user_prompts"
        params = []
        
        if user_id:
            query += " WHERE user_id = ?"
            params.append(user_id)
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        prompts = []
        for row in rows:
            try:
                metadata = json.loads(row[4]) if row[4] else {}
                prompt = UserPrompt(
                    id=row[0],
                    raw_text=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    user_id=row[3],
                    metadata=metadata
                )
                prompts.append(prompt)
            except Exception as e:
                print(f"Error parsing prompt {row[0]}: {e}")
                continue
        
        return prompts
    
    def _get_user_prompts_json(self, limit: Optional[int] = None, user_id: Optional[str] = None) -> List[UserPrompt]:
        """Retrieve user prompts from JSON files."""
        index_file = Path(self.storage_path) / "index.json"
        
        if not index_file.exists():
            return []
        
        with open(index_file, 'r') as f:
            index = json.load(f)
        
        prompts = []
        for item in index["user_prompts"]:
            try:
                prompt_file = Path(self.storage_path) / item["filename"]
                with open(prompt_file, 'r') as f:
                    prompt_data = json.load(f)
                
                # Filter by user_id if specified
                if user_id and prompt_data.get("user_id") != user_id:
                    continue
                
                prompt = UserPrompt(
                    id=prompt_data["id"],
                    raw_text=prompt_data["raw_text"],
                    timestamp=datetime.fromisoformat(prompt_data["timestamp"]),
                    user_id=prompt_data.get("user_id"),
                    metadata=prompt_data.get("metadata", {})
                )
                prompts.append(prompt)
            except Exception as e:
                print(f"Error reading prompt file {item['filename']}: {e}")
                continue
        
        # Sort by timestamp and apply limit
        prompts.sort(key=lambda x: x.timestamp, reverse=True)
        if limit:
            prompts = prompts[:limit]
        
        return prompts
    
    def get_prompt_history(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get prompt history with basic statistics."""
        prompts = self.get_user_prompts(limit=limit, user_id=user_id)
        
        history = []
        for prompt in prompts:
            history.append({
                "id": prompt.id,
                "raw_text": prompt.raw_text[:100] + "..." if len(prompt.raw_text) > 100 else prompt.raw_text,
                "timestamp": prompt.timestamp,
                "user_id": prompt.user_id,
                "length": len(prompt.raw_text),
                "word_count": len(prompt.raw_text.split())
            })
        
        return history
    
    def search_prompts(self, query: str, user_id: Optional[str] = None) -> List[UserPrompt]:
        """Search prompts by text content."""
        prompts = self.get_user_prompts(user_id=user_id)
        
        query_lower = query.lower()
        matching_prompts = []
        
        for prompt in prompts:
            if query_lower in prompt.raw_text.lower():
                matching_prompts.append(prompt)
        
        return matching_prompts
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt and all related data."""
        try:
            if self.storage_type == "sqlite":
                return self._delete_prompt_sqlite(prompt_id)
            elif self.storage_type == "json":
                return self._delete_prompt_json(prompt_id)
            else:
                return False
        except Exception as e:
            print(f"Error deleting prompt: {e}")
            return False
    
    def _delete_prompt_sqlite(self, prompt_id: str) -> bool:
        """Delete prompt from SQLite."""
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()
        
        # Delete related records first
        cursor.execute("DELETE FROM etl_results WHERE original_prompt_id = ?", (prompt_id,))
        cursor.execute("DELETE FROM transformed_prompts WHERE original_prompt_id = ?", (prompt_id,))
        cursor.execute("DELETE FROM user_prompts WHERE id = ?", (prompt_id,))
        
        conn.commit()
        conn.close()
        return True
    
    def _delete_prompt_json(self, prompt_id: str) -> bool:
        """Delete prompt from JSON storage."""
        index_file = Path(self.storage_path) / "index.json"
        
        if not index_file.exists():
            return False
        
        with open(index_file, 'r') as f:
            index = json.load(f)
        
        # Find and remove prompt files
        for collection in ["user_prompts", "transformed_prompts", "etl_results"]:
            items_to_remove = []
            for item in index[collection]:
                if item["id"] == prompt_id or item["id"].startswith(prompt_id):
                    items_to_remove.append(item)
                    # Remove the file
                    file_path = Path(self.storage_path) / item["filename"]
                    if file_path.exists():
                        file_path.unlink()
            
            # Remove from index
            for item in items_to_remove:
                index[collection].remove(item)
        
        # Save updated index
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        return True
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            if self.storage_type == "sqlite":
                return self._get_storage_stats_sqlite()
            elif self.storage_type == "json":
                return self._get_storage_stats_json()
            else:
                return {"error": "Unknown storage type"}
        except Exception as e:
            return {"error": str(e)}
    
    def _get_storage_stats_sqlite(self) -> Dict[str, Any]:
        """Get SQLite storage statistics."""
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM user_prompts")
        prompt_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM transformed_prompts")
        transformed_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM etl_results")
        result_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_prompts WHERE user_id IS NOT NULL")
        user_prompt_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "storage_type": "sqlite",
            "total_prompts": prompt_count,
            "total_transformed": transformed_count,
            "total_results": result_count,
            "user_prompts": user_prompt_count,
            "anonymous_prompts": prompt_count - user_prompt_count
        }
    
    def _get_storage_stats_json(self) -> Dict[str, Any]:
        """Get JSON storage statistics."""
        index_file = Path(self.storage_path) / "index.json"
        
        if not index_file.exists():
            return {"storage_type": "json", "total_prompts": 0}
        
        with open(index_file, 'r') as f:
            index = json.load(f)
        
        return {
            "storage_type": "json",
            "total_prompts": len(index["user_prompts"]),
            "total_transformed": len(index["transformed_prompts"]),
            "total_results": len(index["etl_results"])
        }
