export default {
  template: `
    <div v-if="loading === false">
      <h2 class="title">DB Queries</h2>

      <table class="query-table">
        <thead>
          <tr>
            <th>Query</th>
            <th>Query Time</th>
            <th>Happened</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="query in dbQueries" :key="query.id" @click="goToQueryDetails(query.id)">
            <td class="width-100" v-if="query.db_query.length < 200">{{ query.db_query }}</td>
            <td class="width-100" v-else>
              <span :title="query.db_query">{{ query.db_query.substring(0, 200) + '...' }}</span>
            </td>
            <td>{{ query.db_query_time }} ms</td>
            <td>
              <span :title="formatFullDatetime(query.created_at)">
                {{ formatRelativeTime(query.created_at) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination-controls">
        <button class="pagination-btn" @click="prevPage" :disabled="page <= 1">Previous</button>
        <span class="pagination-info">Page {{ page }} of {{ totalPages }}</span>
        <button class="pagination-btn" @click="nextPage" :disabled="page >= totalPages">Next</button>
      </div>
    </div>

    <div v-else>
      <h2 class="title">Loading...</h2>
    </div>
  `,
  data() {
    return {
      dbQueries: [],
      loading: true,
      page: 1,
      size: 10,
      totalPages: 1
    };
  },
  watch: {
    '$route.query.page': {
      immediate: true,
      handler(newVal) {
        const newPage = parseInt(newVal) || 1;
        if (newPage !== this.page) {
          this.page = newPage;
          this.fetchQueries();
        }
      }
    }
  },
  mounted() {
    this.fetchQueries();
  },
  methods: {
    async fetchQueries() {
      this.loading = true;
      try {
        const response = await axios.get('/db-queries/', {
          params: {
            page: this.page,
            size: this.size
          }
        });
        this.dbQueries = response.data.items;
        this.totalPages = response.data.pages;
      } catch (error) {
        console.error('Error fetching DB queries:', error);
      } finally {
        this.loading = false;
      }
    },
    changePage(newPage) {
      if (newPage !== this.page && newPage >= 1 && newPage <= this.totalPages) {
        this.$router.push({
          name: "db-queries",
          query: { ...this.$route.query, page: newPage }
        });
      }
    },
    nextPage() {
      this.changePage(this.page + 1);
    },
    prevPage() {
      this.changePage(this.page - 1);
    },
    goToQueryDetails(queryId) {
      this.$router.push({ name: 'db-query-detail', params: { id: queryId } });
    },
    formatRelativeTime(datetime) {
      const userTimezone = dayjs.tz.guess();
      return dayjs.utc(datetime).tz(userTimezone).fromNow();
    },
    formatFullDatetime(datetime) {
      const userTimezone = dayjs.tz.guess();
      return dayjs.utc(datetime).tz(userTimezone).format("YYYY-MM-DD HH:mm:ss [Z]");
    }
  }
};