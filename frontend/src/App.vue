<template>
  <div class="app-container">
    <header>
      <h1>🚀 AI News Reporter</h1>
    </header>

    <!-- Filter Panel -->
    <div class="filter-container">
      <!-- Publication Filters -->
      <nav class="filter-group">
        <div class="filter-label">Publications</div>
        <div class="filter-buttons">
          <button 
            v-for="pub in publications" 
            :key="pub.id" 
            @click="filterByPublication(pub.id)"
            :class="{ active: activePublication === pub.id }"
          >
            {{ pub.label }}
          </button>
          <button 
            @click="filterByPublication('all')" 
            :class="{ active: activePublication === 'all' }"
          >
            All Pubs
          </button>
        </div>
      </nav>

      <!-- Category Filters -->
      <nav v-if="newsData" class="filter-group">
        <div class="filter-label">Categories</div>
        <div class="filter-buttons">
          <button 
            v-for="cat in categories" 
            :key="cat.id" 
            @click="filterByCategory(cat.id)"
            :class="{ active: activeCategory === cat.id }"
          >
            {{ cat.label }}
          </button>
          <button 
            @click="filterByCategory('all')" 
            :class="{ active: activeCategory === 'all' }"
          >
            All Categories
          </button>
        </div>
      </nav>
    </div>

    <main v-if="newsData">
      <!-- Date Groups -->
      <div v-for="date in sortedDates" :key="date" class="edition">
        <div class="date-header">{{ date }}</div>
        
        <!-- Sender Groups -->
        <div v-for="pub in publications" :key="pub.id" class="pub-group">
          <template v-if="hasArticlesForPubAndDate(date, pub.id)">
            <div class="pub-header">
              <span class="pub-badge">{{ pub.label }}</span>
            </div>
            
            <div class="grid">
              <div v-for="item in getArticlesForPubDateAndCategory(date, pub.id)" :key="item.id" class="card">
                <div class="card-content">
                  {{ item.content }}
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Pagination / Load More -->
      <div v-if="hasMore" class="load-more">
        <button @click="loadMore" :disabled="loadingMore">
          {{ loadingMore ? 'Loading...' : 'Load More' }}
        </button>
      </div>
    </main>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else class="loading">Loading news...</div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';

const newsData = ref(null);
const error = ref(null);
const activeCategory = ref('all');
const activePublication = ref('all');
const visibleDays = ref(3);
const loadingMore = ref(false);

const publications = computed(() => {
  if (!newsData.value) return [];
  const senders = [...new Set(newsData.value.map(item => item.sender))].filter(Boolean);
  return senders.map(sender => ({ id: sender, label: sender }));
});

const categories = [
  { id: 'headlines', label: '📰 Headlines' },
  { id: 'deep_dives', label: '🔍 Deep Dives' },
  { id: 'engineering', label: '🛠️ Engineering' },
  { id: 'misc', label: '✨ Misc' },
];

const filteredSections = computed(() => {
  if (activeCategory.value === 'all') return categories;
  return categories.filter(c => c.id === activeCategory.value);
});

const filteredNews = computed(() => {
  if (!newsData.value) return [];
  let data = [...newsData.value];
  if (activePublication.value !== 'all') {
    data = data.filter(item => item.sender === activePublication.value);
  }
  return data.sort((a, b) => {
    const dateA = new Date(a.email_date || 0);
    const dateB = new Date(b.email_date || 0);
    return dateB - dateA;
  });
});

const sortedDates = computed(() => {
  if (!filteredNews.value) return [];
  const allDates = [...new Set(filteredNews.value.map(e => e.email_date))].filter(Boolean);
  return allDates.sort((a, b) => new Date(b) - new Date(a)).slice(0, visibleDays.value);
});

function getArticlesForPubDateAndCategory(date, pubId, catId) {
  if (!filteredNews.value) return [];
  return filteredNews.value.filter(item => 
    item.email_date === date && 
    item.sender === pubId
  );
}

function hasArticlesForPubAndDate(date, pubId) {
  if (!filteredNews.value) return false;
  return filteredNews.value.some(item => item.email_date === date && item.sender === pubId);
}

const hasMore = computed(() => {
  if (!newsData.value) return false;
  const allDates = [...new Set(newsData.value.map(e => e.email_date))].filter(Boolean);
  return visibleDays.value < allDates.length;
});

function filterByCategory(catId) {
  activeCategory.value = catId;
}

function filterByPublication(pubId) {
  activePublication.value = pubId;
}

async function loadMore() {
  loadingMore.value = true;
  await new Promise(resolve => setTimeout(resolve, 500));
  visibleDays.value += 3;
  loadingMore.value = false;
}

onMounted(async () => {
  try {
    const response = await fetch('http://localhost:8000/news');
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    newsData.value = await response.json();
  } catch (e) {
    console.error('Fetch error:', e);
    error.value = `Error loading news data: ${e.message}`;
  }
});
</script>

<style>
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: #f4f7f6;
  color: #333;
  margin: 0;
  padding: 0;
}
.app-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}
header {
  text-align: center;
  margin-bottom: 2rem;
}
header h1 {
  font-size: 2.5rem;
  color: #1a1a1a;
  margin: 0;
}
.filter-group {
  margin-bottom: 2rem;
  text-align: center;
}
.filter-label {
  font-weight: bold;
  margin-bottom: 0.5rem;
  display: block;
}
.filter-buttons {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.filter-buttons button {
  padding: 0.5rem 1rem;
  border-radius: 15px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}
.filter-buttons button.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}
.edition {
  margin-bottom: 4rem;
}
.date-header {
  font-size: 1.8rem;
  font-weight: bold;
  border-bottom: 3px solid #333;
  padding-bottom: 0.5rem;
  margin-bottom: 2rem;
  color: #222;
}
.pub-group {
  margin-bottom: 2.5rem;
}
.pub-header {
  margin-bottom: 1rem;
}
.pub-badge {
  background: #eee;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-weight: bold;
  font-size: 1rem;
  color: #444;
  border: 1px solid #ddd;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}
.card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  transition: transform 0.2s;
  border: 1px solid #eee;
}
.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.card-content {
  font-size: 0.95rem;
  line-height: 1.5;
  color: #555;
}
.load-more {
  display: flex;
  justify-content: center;
  margin: 3rem 0;
}
.load-more button {
  padding: 0.8rem 2rem;
  font-size: 1rem;
  border-radius: 8px;
  border: none;
  background: #007bff;
  color: white;
  cursor: pointer;
  transition: opacity 0.2s;
}
.load-more button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error {
  color: #d9534f;
  text-align: center;
  padding: 2rem;
  background: #fdf7f7;
  border-radius: 8px;
  border: 1px solid #d9534f;
}
.loading {
  text-align: center;
  font-size: 1.2rem;
  color: #888;
}
</style>
