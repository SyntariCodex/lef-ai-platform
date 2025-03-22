import sqlite3
import threading
import queue
import logging
from datetime import datetime
import json
from typing import Dict, Optional, List
import time

class ChatPersistence:
    def __init__(self, db_path: str = "lef_chat.db"):
        self.db_path = db_path
        self.message_queue = queue.Queue()
        self.processing = False
        self.background_thread = None
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('LEF.ChatPersistence')
        
        # Initialize database
        self._initialize_db()
        
        # Start background processing
        self.start_background_processing()
        
    def _initialize_db(self):
        """Initialize SQLite database for chat persistence"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Create tables with error handling
            c.execute('''CREATE TABLE IF NOT EXISTS chat_sessions
                        (session_id TEXT PRIMARY KEY,
                         start_time TIMESTAMP,
                         end_time TIMESTAMP,
                         status TEXT,
                         metadata TEXT)''')
                        
            c.execute('''CREATE TABLE IF NOT EXISTS messages
                        (message_id INTEGER PRIMARY KEY,
                         session_id TEXT,
                         timestamp TIMESTAMP,
                         role TEXT,
                         content TEXT,
                         context TEXT,
                         status TEXT,
                         FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id))''')
            
            # Add indexes for better performance
            c.execute('CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Database initialized successfully")
            
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization failed: {str(e)}")
            raise
            
    def start_background_processing(self):
        """Start background thread for processing messages"""
        if self.processing:
            return
            
        self.processing = True
        self.background_thread = threading.Thread(
            target=self._process_message_queue,
            daemon=True
        )
        self.background_thread.start()
        self.logger.info("Background processing started")
        
    def stop_background_processing(self):
        """Stop background thread for processing messages"""
        self.processing = False
        if self.background_thread:
            self.background_thread.join()
        self.logger.info("Background processing stopped")
        
    def _process_message_queue(self):
        """Process messages from the queue"""
        while self.processing:
            try:
                # Get message from queue with timeout
                message = self.message_queue.get(timeout=1)
                
                try:
                    self._save_message_to_db(message)
                except Exception as e:
                    self.logger.error(f"Failed to save message: {str(e)}")
                    # Put message back in queue for retry
                    self.message_queue.put(message)
                    
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in message processing: {str(e)}")
                time.sleep(1)  # Wait before retrying
                
    def _save_message_to_db(self, message: Dict):
        """Save message to database with error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Check if session exists
            c.execute('SELECT 1 FROM chat_sessions WHERE session_id = ?',
                     (message['session_id'],))
            if not c.fetchone():
                # Create new session
                c.execute('''INSERT INTO chat_sessions 
                            (session_id, start_time, status, metadata)
                            VALUES (?, ?, ?, ?)''',
                         (message['session_id'],
                          message['timestamp'],
                          'active',
                          json.dumps(message.get('metadata', {}))))
            
            # Insert message
            c.execute('''INSERT INTO messages 
                        (session_id, timestamp, role, content, context, status)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (message['session_id'],
                      message['timestamp'],
                      message['role'],
                      message['content'],
                      json.dumps(message.get('context', {})),
                      'processed'))
            
            conn.commit()
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
                
    def save_message(self, session_id: str, role: str, content: str,
                    context: Optional[Dict] = None, metadata: Optional[Dict] = None):
        """Queue message for saving"""
        message = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'role': role,
            'content': content,
            'context': context or {},
            'metadata': metadata or {}
        }
        
        try:
            self.message_queue.put(message)
        except Exception as e:
            self.logger.error(f"Failed to queue message: {str(e)}")
            
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Retrieve chat history for a session"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''SELECT timestamp, role, content, context, status
                        FROM messages
                        WHERE session_id = ?
                        ORDER BY timestamp''', (session_id,))
            
            history = []
            for row in c.fetchall():
                history.append({
                    'timestamp': row[0],
                    'role': row[1],
                    'content': row[2],
                    'context': json.loads(row[3]),
                    'status': row[4]
                })
                
            return history
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to retrieve history: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()
                
    def close_session(self, session_id: str):
        """Close a chat session"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''UPDATE chat_sessions 
                        SET end_time = ?, status = 'closed'
                        WHERE session_id = ?''',
                     (datetime.now().isoformat(), session_id))
            
            conn.commit()
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to close session: {str(e)}")
        finally:
            if conn:
                conn.close() 