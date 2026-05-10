<template>
  <div class="app-container">
    <header>
      <h1>🚀 AI News Reporter</h1>
    </header>

    <!-- Category Navigation Panel -->
    <nav v-if="newsData" class="category-nav">
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
        All
      </button>
    </nav>

    <main v-if="newsData">
      <!-- Date Groups -->
      <div v-for="date in sortedDates" :key="date" class="edition">
        <div class="date-header">{{ date }}</div>
        
        <!-- Main Publication Groups (TLDR AI, TLDR DEV, etc.) -->
        <div v-for="pub in publications" :key="pub.id" class="pub-group">
          <template v-if="hasArticlesForPubAndDate(date, pub.id)">
            <div class="pub-header">
              <span class="pub-badge">{{ pub.label }}</span>
            </div>
            
            <!-- Section-based articles within the publication -->
            <div v-for="section in filteredSections" :key="section.id" class="section-group">
              <template v-if="getArticlesForPubDateAndCategory(date, pub.id, section.id).length">
                <h3 v-if="section.label">{{ section.label }}</h3>
                <div class="grid">
                  <div v-for="item in getArticlesForPubDateAndCategory(date, pub.id, section.id)" :key="item.title" class="card">
                    <a :href="item.url" target="_blank">{{ item.title }}</a>
                    <p>{{ item.summary }}</p>
                  </div>
                </div>
              </template>
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
const visibleDays = ref(3);
const loadingMore = ref(false);

// TLDR Main Publication Groups
const publications = [
  { id: 'tldrai', label: '🤖 TLDR AI' },
  { id: 'tldrdev', label: '💻 TLDR DEV' },
  { id: 'tldrinfosec', label: '🛡️ TLDR InfoSec' },
  { id: 'tldrmarketing', label: '📈 TLDR Marketing' },
  { id: 'tldrdesign', label: '🎨 TLDR Design' },
  { id: 'tldrfintech', label: '💰 TLDR FinTech' },
  { id: 'tldrproduct', label: '📦 TLDR Product' },
  { id: 'tldrfounders', label: '🚀 TLDR Founders' },
  { id: 'tldrcrypto', label: '🪙 TLDR Crypto' },
  { id: 'tldrnewsletter', label: '📩 TLDR General' },
];

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

const sortedDates = computed(() => {
  if (!newsData.value) return [];
  const allDates = [...new Set(newsData.value.map(e => e.date))];
  // Sort descending (newest first)
  return allDates.sort((a, b) => (a === 'Unknown date' ? 1 : b.localeCompare(a))).slice(0, visibleDays.value);
});

function getArticlesForPubDateAndCategory(date, pubId, catId) {
  if (!newsData.value) return [];
  const articles = [];
  newsData.value.forEach(edition => {
    // Check if the edition matches date AND the article URL matches the publication ID (from utm_source)
    if (edition.date === date && edition[catId]) {
      const filtered = edition[catId].filter(item => item.url.includes(`utm_source=${pubId}`));
      articles.push(...filtered);
    }
  });
  return articles;
}

function hasArticlesForPubAndDate(date, pubId) {
  if (!newsData.value) return false;
  return newsData.value.some(edition => {
    if (edition.date !== date) return false;
    return Object.values(edition).some(catList => 
      Array.isArray(catList) && catList.some(item => item.url.includes(`utm_source=${pubId}`))
    );
  });
}

const hasMore = computed(() => {
  if (!newsData.value) return false;
  const allDates = [...new Set(newsData.value.map(e => e.date))];
  return visibleDays.value < allDates.length;
});

function filterByCategory(catId) {
  activeCategory.value = catId;
}

async function loadMore() {
  loadingMore.value = true;
  await new Promise(resolve => setTimeout(resolve, 500));
  visibleDays.value += 3;
  loadingMore.value = false;
}

onMounted(async () => {
  try {
    const response = await fetch('/news-reporter/news_structured.json');
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
  font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif;
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

.category-nav {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 3rem;
  flex-wrap: wrap;
}
.category-nav button {
  padding: 0.6rem 1.2rem;
  border-radius: 20px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}
.category-nav button.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}
.category-nav button:hover:not(.active) {
  background: #eef;
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
.section-group h3 {
  font-size: 1.1rem;
  margin-bottom: 1rem;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.05em;
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
.card a {
  font-weight: bold;
  color: #007bff;
  text-decoration: none;
  font-size: 1.1rem;
  display: block;
  margin-bottom: 0.5rem;
}
.card p {
  font-size: 0.95rem;
  line-height: 1.5;
  color: #555;
  margin: 0;
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
