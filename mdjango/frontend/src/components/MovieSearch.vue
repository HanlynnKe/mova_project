<!--suppress ALL -->
<template>
  <div id="diagram-select">
    <main-header></main-header>
    <el-container>
      <el-header></el-header>

      <el-main>
        <el-alert class="alert-msg"
                  title="Search & Show"
                  type="info" show-icon
                  :closable="false">
        </el-alert>
        <el-form class="search-form" label-width="80px">
          <el-form-item>
            <el-row class="search-ipt">
              <el-col :span="4">
                <el-select v-model="searchOption" placeholder="请选择">
                  <el-option v-for="item in optionList"
                             :key="item.value" :label="item.label" :value="item.value">
                  </el-option>
                </el-select>
              </el-col>
              <el-col :span="15" :push="2">
                <el-input v-model="searchObject"
                          placeholder="请输入您想搜索的内容" clearable></el-input>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item>
            <el-scrollbar  class="view-info">
              <div>
                <ul class="movie-list">
                  <li v-for="(movie, index) in this.movieList" :key="index">
                    <table>
                      <tr>
                        <th class="short">电影名</th>
                        <th class="short">类型</th>
                        <th class="short">导演</th>
                        <th class="short">上映日期</th>
                        <th class="short">票房</th>
                        <th class="short">评分</th>
                      </tr>
                      <tr>
                        <td class="short">{{movie.name}}</td>
                        <td class="short">{{movie.type}}</td>
                        <td class="short">{{movie.director}}</td>
                        <td class="short">{{movie.date}}</td>
                        <td class="short">{{movie.boxoffice}}万</td>
                        <td class="short">{{movie.score}}</td>
                      </tr>
                    </table>
                    <table>
                      <tr>
                        <th class="short">主演</th>
                        <td class="long">{{movie.actor}}</td>
                      </tr>
                    </table>
                  </li>
                </ul>
              </div>
            </el-scrollbar>
          </el-form-item>
        </el-form>
      </el-main>

      <el-footer>
        <el-row :type="'flex'">
          <el-col :span="12" align="center">
            <div class="download">
              <el-button class="search-btn" @click="startSearch" round>搜索</el-button>
            </div>
          </el-col>
          <el-col :span="12" align="center">
            <div class="cancel">
              <el-button class="cancel-btn" @click="toMainPage" round>返回</el-button>
            </div>
          </el-col>
        </el-row>
        <h6 align="center" style="color: #ffffff">Copyright © Software Engineering Group X</h6>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import MainHeader from './MainHeader'

export default {
  components: {
    'main-header': MainHeader
  },
  data () {
    return {
      searchObject: '',
      searchOption: '',
      optionList: [
        {value: 'name', label: '电影'},
        {value: 'director', label: '导演'},
        {value: 'actor', label: '演员'}
      ],
      movie: {},
      movieList: []
    }
  },
  methods: {
    startSearch: function () {
      var searchRequest = {
        a: 1,
        film: '0',
        director: '0',
        actor: '0'
      }
      if (this.searchOption === 'name') {
        searchRequest.film = this.searchObject
      } else if (this.searchOption === 'director') {
        searchRequest.director = this.searchObject
      } else {
        searchRequest.actor = this.searchObject
      }
      var result = []
      var postData = this.$qs.stringify(searchRequest)
      this.axios.post('movie/', postData).then(function (response) {
        // console.log(response.data)
        for (var item in response.data) {
          result.push(response.data[item])
        }
      }).catch(function (error) {
        console.log(error)
      })
      this.movieList = result
    },
    toMainPage: function () {
      this.$router.push({path: '/main'})
    }
  }
}
</script>

<style scoped>
#diagram-select {
  background: #2d3436;
  max-width: 800px;
  margin: 0 auto;
}
.search-form {
  background: white;
  border: solid 5px #20bf6b;
  border-radius: 10px;
}
.el-main {
  margin-top: 10px;
}
.el-footer {
  background-color: #747d8c;
  color: #333;
  line-height: 60px;
  margin-top: 0px;
  margin-bottom: 20px;
}
h1 {
  color: white;
  font-family: Monaco,monospace;
  margin-top: 1px;
}
h4, h5{
  color: white;
  font-family: "Hiragino Sans GB",monospace;
}
.search-btn {
  color: #dfe6e9;
  border-color: #20bf6b;
  border-width: 3px;
  background: #747d8c;
}
.cancel-btn {
  color: #dfe6e9;
  border-color: #20bf6b;
  border-width: 3px;
  background: #747d8c;
}
.search-ipt {
  margin-top: 20px;
  margin-bottom: 10px;
}
.alert-msg {
  margin-bottom: 10px;
}
.view-info {
  color: #2f3542;
  border: solid 3px #20bf6b;
  box-sizing: content-box;
  margin-right: 70px;
  width: 550px;
  height: 200px;
  line-height: 25px;
}
.short {
  width: 80px;
}
.long {
  width: 600px;
}
</style>
