<template>
  <div class="app-container">
    <header>
      <h1>🚀 AI News Reporter</h1>
      <p>Curated insights from TLDR AI</p>
    </header>

    <main v-if="newsData">
      <div v-for="(edition, index) in newsData" :key="index" class="edition">
        <div class="date-header">{{ edition.date }}</div>
        
        <section v-if="edition.headlines.length">
          <h3>📰 Top Headlines</h3>
          <div class="grid">
            <div v-for="item in edition.headlines" :key="item.title" class="card">
              <a :href="item.url" target="_blank">{{ item.title }}</a>
              <p>{{ item.summary }}</p>
            </div>
          </div>
        </section>

        <section v-if="edition.deep_dives.length">
          <h3>🔍 Deep Dives</h3>
          <div class="grid">
            <div v-for="item in edition.deep_dives" :key="item.title" class="card">
              <a :href="item.url" target="_blank">{{ item.title }}</a>
              <p>{{ item.summary }}</p>
            </div>
          </div>
        </section>

        <section v-if="edition.engineering.length">
          <h3>🛠️ Engineering & Tools</h3>
          <div class="grid">
            <div v-for="item in edition.engineering" :key="item.title" class="card">
              <a :href="item.url" target="_blank">{{ item.title }}</a>
              <p>{{ item.summary }}</p>
            </div>
          </div>
        </section>
      </div>
    </main>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else class="loading">Loading news...</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const newsData = ref(null);
const error = ref(null);

onMounted(async () => {
  try {
    // CRITICAL FIX: Use absolute path relative to the base of the gh-pages site
    const response = await fetch('/news-reporter/news_structured.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
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
  margin-bottom: 3rem;
}
header h1 {
  font-size: 2.5rem;
  color: #1a1a1a;
}
.edition {
  margin-bottom: 4rem;
}
.date-header {
  font-size: 1.5rem;
  font-weight: bold;
  border-bottom: 2px solid #ddd;
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
  color: #666;
}
section h3 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: #444;
  display: flex;
  align-items: center;
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
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}
.card:hover {
  transform: translateY(-3px);
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
