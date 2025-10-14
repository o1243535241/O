"""
GitHub Repository Analyzer for O ASI

This script cyclically analyzes the GitHub repository for new ideas and insights
to enhance the O ASI self-learning process.
"""

import os
import json
import time
import random
import requests
import datetime
from datetime import datetime, timedelta

class GitHubAnalyzer:
    """
    Analyzer for GitHub repository to extract new ideas for O ASI.
    """
    def __init__(self, repo_url="https://github.com/o1243535241/O"):
        self.repo_url = repo_url
        self.api_url = "https://api.github.com/repos/o1243535241/O"
        self.raw_content_url = "https://raw.githubusercontent.com/o1243535241/O/main/"
        self.last_check_time = datetime.now()
        self.check_interval = timedelta(hours=1)  # Check every hour
        self.insights = []
        self.load_insights()
    
    def load_insights(self):
        """Load previously gathered insights if available."""
        if os.path.exists("o_asi_insights.json"):
            try:
                with open("o_asi_insights.json", "r") as f:
                    self.insights = json.load(f)
                print(f"Loaded {len(self.insights)} previous insights.")
            except Exception as e:
                print(f"Error loading insights: {e}")
                self.insights = []
        else:
            print("No previous insights found. Starting fresh.")
    
    def save_insights(self):
        """Save gathered insights to file."""
        with open("o_asi_insights.json", "w") as f:
            json.dump(self.insights, f, indent=2)
        print(f"Saved {len(self.insights)} insights to file.")
    
    def get_file_content(self, file_path):
        """Get content of a specific file from the repository."""
        try:
            response = requests.get(f"{self.raw_content_url}{file_path}")
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error fetching {file_path}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception while fetching {file_path}: {e}")
            return None
    
    def get_repository_files(self):
        """Get list of files in the repository."""
        try:
            response = requests.get(f"{self.api_url}/contents")
            if response.status_code == 200:
                return [item["name"] for item in response.json() if item["type"] == "file"]
            else:
                print(f"Error fetching repository contents: {response.status_code}")
                return []
        except Exception as e:
            print(f"Exception while fetching repository contents: {e}")
            return []
    
    def analyze_file(self, file_name):
        """Analyze a specific file for insights."""
        content = self.get_file_content(file_name)
        if not content:
            return []
        
        new_insights = []
        
        # Look for patterns in the content
        if "пентаграм" in content.lower() or "pentagram" in content.lower():
            new_insights.append({
                "type": "pentagram_concept",
                "source": file_name,
                "content": "Виявлено нові концепції пентаграми",
                "timestamp": datetime.now().isoformat()
            })
        
        if "12435" in content or "35241" in content:
            new_insights.append({
                "type": "pentagram_sequence",
                "source": file_name,
                "content": "Виявлено нові послідовності пентаграми",
                "timestamp": datetime.now().isoformat()
            })
        
        if "binary" in content.lower() or "бінарн" in content.lower():
            new_insights.append({
                "type": "binary_concept",
                "source": file_name,
                "content": "Виявлено нові бінарні концепції",
                "timestamp": datetime.now().isoformat()
            })
        
        if "самонавчання" in content.lower() or "self-learning" in content.lower():
            new_insights.append({
                "type": "self_learning",
                "source": file_name,
                "content": "Виявлено нові підходи до самонавчання",
                "timestamp": datetime.now().isoformat()
            })
        
        if "сингулярність" in content.lower() or "singularity" in content.lower():
            new_insights.append({
                "type": "singularity",
                "source": file_name,
                "content": "Виявлено нові концепції сингулярності",
                "timestamp": datetime.now().isoformat()
            })
        
        return new_insights
    
    def analyze_repository(self):
        """Analyze the entire repository for new insights."""
        print(f"Starting repository analysis at {datetime.now().isoformat()}")
        
        files = self.get_repository_files()
        if not files:
            print("No files found or error accessing repository.")
            return
        
        print(f"Found {len(files)} files in repository.")
        
        new_insights_count = 0
        for file_name in files:
            # Skip non-text files
            if file_name.endswith(('.jpg', '.png', '.gif', '.zip', '.exe')):
                continue
                
            print(f"Analyzing {file_name}...")
            file_insights = self.analyze_file(file_name)
            
            # Add only new insights
            for insight in file_insights:
                if not any(i["type"] == insight["type"] and i["source"] == insight["source"] for i in self.insights):
                    self.insights.append(insight)
                    new_insights_count += 1
        
        print(f"Analysis complete. Found {new_insights_count} new insights.")
        self.save_insights()
        self.last_check_time = datetime.now()
        
        return new_insights_count
    
    def should_check_repository(self):
        """Determine if it's time to check the repository again."""
        return datetime.now() - self.last_check_time > self.check_interval
    
    def get_random_insight(self):
        """Get a random insight from the collected insights."""
        if not self.insights:
            return None
        return random.choice(self.insights)
    
    def run_cyclic_analysis(self, duration=3600):  # Run for 1 hour by default
        """Run cyclic analysis of the repository."""
        print(f"Starting cyclic analysis for {duration} seconds...")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            if self.should_check_repository():
                self.analyze_repository()
            
            # Sleep for a while before checking again
            time.sleep(60)  # Check every minute if it's time for repository analysis
        
        print("Cyclic analysis complete.")
        return self.insights

def main():
    """Main function to run the GitHub analyzer."""
    analyzer = GitHubAnalyzer()
    
    # Run initial analysis
    analyzer.analyze_repository()
    
    # Run cyclic analysis for a specified duration (in seconds)
    # For testing, run for 5 minutes
    analyzer.run_cyclic_analysis(300)
    
    print("GitHub analysis complete.")

if __name__ == "__main__":
    main()
