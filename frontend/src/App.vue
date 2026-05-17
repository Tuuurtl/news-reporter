<template>
  <div class="app-container">
    <header>
      <h1>🚀 AI News Reporter</h1>
    </header>

    <!-- SCREEN 1: Sender Selection -->
    <div v-if="!selectedPublication" class="selection-screen">
      <div class="selection-grid">
        <div 
          v-for="pub in publications" 
          :key="pub.id" 
          class="pub-card" 
          @click="selectedPublication = pub.id"
        >
          <div class="pub-icon">📰</div>
          <div class="pub-label">{{ pub.label }}</div>
          <div class="pub-count">{{ pub.count }} Articles</div>
        </div>
      </div>
      <div class="back-button" v-if="selectedPublication" @click="selectedPublication = null">
        Back to Selection
      </div>
    </div>

    <!-- SCREEN 2: News Feed -->
    <div v-else class="feed-screen">
      <nav class="top-nav">
        <button @click="selectedPublication = null" class="back-btn">← Back</button>
        <div class="current-pub">{{ selectedPublicationLabel }}</div>
      </nav>

      <div v-if="filteredNews.length" class="news-list">
        <div v-for="item in filteredNews" :key="item.id" class="news-date-group">
          <div class="date-separator">
            {{ formatDate(item.email_date) }}
          </div>
          <div class="articles-grid">
            <a 
              v-for="article in item.articles" 
              :key="article.title" 
              :href="article.link" 
              target="_blank"
              class="article-card"
            >
              <div class="article-title">{{ article.title }}</div>
              <div class="article-desc">{{ article.description }}</div>
            </a>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        No articles found for this publication.
      </div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-else-if="!newsData" class="loading">Loading news...</div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';

const newsData = ref(null);
const error = ref(null);
const selectedPublication = ref(null);

const publications = computed(() => {
  if (!newsData.value) return [];
  const pubMap = {};
  newsData.value.forEach(item => {
    if (item.sender) {
      const count = item.articles ? item.articles.length : 0;
      pubMap[item.sender] = (pubMap[item.sender] || 0) + count;
    }
  });
  return Object.entries(pubMap).map(([id, count]) => ({
    id,
    label: id,
    count
  }));
});

const selectedPublicationLabel = computed(() => {
  return selectedPublication.value;
});

const filteredNews = computed(() => {
  if (!newsData.value) return [];
  return newsData.value
    .filter(item => item.sender === selectedPublication.value)
    .sort((a, b) => new Date(b.email_date) - new Date(a.email_date));
});

function formatDate(dateStr) {
  if (!dateStr) return 'Unknown Date';
  return new Date(dateStr).toLocaleDateString(undefined, { 
    year: 'numeric', month: 'long', day: 'numeric' 
  });
}

onMounted(async () => {
  try {
    const response = await fetch('./news_structured.json');
    if (!response.ok) throw new Error('Failed to load news data');
    newsData.value = await response.json();
  } catch (e) {
    error.value = e.message;
  }
});
</script>

<style>
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: #f8f9fa;
  color: #212529;
  margin: 0;
  padding: 0;
}
.app-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem 1rem;
}
header {
  text-align: center;
  margin-bottom: 3rem;
}
header h1 {
  font-size: 2.2rem;
  color: #1a1a1a;
}

/* Selection Screen */
.selection-screen {
  animation: fadeIn 0.3s ease;
}
.selection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}
.pub-card {
  background: white;
  padding: 2rem 1rem;
  border-radius: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #e0e0e0;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.pub-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.1);
  border-color: #007bff;
}
.pub-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}
.pub-label {
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}
.pub-count {
  font-size: 0.9rem;
  color: #6c757d;
}

/* Feed Screen */
.feed-screen {
  animation: fadeIn 0.3s ease;
}
.top-nav {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}
.back-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}
.current-pub {
  font-size: 1.4rem;
  font-weight: bold;
}

/* New Grid Layout Styles */
.news-date-group {
  margin-bottom: 3rem;
}
.date-separator {
  font-size: 1.1rem;
  font-weight: bold;
  color: #6c757d;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #dee2e6;
}
.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}
.article-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
  border: 1px solid #eee;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.article-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.1);
  border-color: #007bff;
}
.article-title {
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
  color: #1a1a1a;
  line-height: 1.3;
}
.article-desc {
  font-size: 0.95rem;
  line-height: 1.5;
  color: #495057;
  flex-grow: 1;
}

.error {
  color: #d9534f;
  text-align: center;
  padding: 2rem;
}
.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #888;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
