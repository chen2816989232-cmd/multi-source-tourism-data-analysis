/**
 * @description: 路由页面列表
 */

const ListPage = () => import("@/views/list/list.vue");

const routes = [
  {
    path: '/',
    component: () => import('@/views/layout/layout.vue'),
    redirect: '/login',
    children: [
      {
        path: '/home',
        component: () => import('@/views/home/home.vue'),
        meta: {
          title: '首页'
        },        
      },
      {
        path: '/center',
        component: () => import('@/views/center.vue'),
        meta: {
          title: '个人信息'
        },
      },
      {
        path: '/updatePassword',
        component: () => import('@/views/updatePassword.vue'),
        meta: {
          title: '修改密码',
        },
      },
      {
        path: '/board',
        component: () => import("@/views/decision/DecisionBoard.vue"),
        meta: {
          title: "鍒嗘瀽鍐崇瓥",
        },
      },
      {
        path: '/config/:type',
        component: ListPage,
      },
      {
        path: '/ctripjd',
        component: ListPage,
        meta: {
          title: "景点查询",
        },        
      },  
      {
        path: '/ctrippinglun',
        component: ListPage,
        meta: {
          title: "景点评论",
        },        
      },  
      {
        path: '/yonghu',
        component: ListPage,
        meta: {
          title: "用户",
        },        
      },  
      {
        path: '/ctripjdforecast',
        component: ListPage,
        meta: {
          title: "景点热度预测",
        },        
      },  
      {
        path: '/ctripjdforecast1',
        component: ListPage,
        meta: {
          title: "地区预测",
        },        
      },  
      {
        path: '/qingganfenxi',
        component: ListPage,
        meta: {
          title: "情感分析",
        },        
      },  
      {
        path: '/lvyoushuju',
        component: ListPage,
        meta: {
          title: "旅游数据",
        },        
      },  
      {
        path: '/news',
        component: ListPage,
        meta: {
          title: "系统公告",
        },        
      },  
      {
        path: '/storeup',
        component: ListPage,
        meta: {
          title: "收藏表",
        },        
      },  
      {
        path: '/systemintro',
        component: ListPage,
        meta: {
          title: "系统简介",
        },        
      },  
      {
        path: '/smsregistercode',
        component: ListPage,
        meta: {
          title: "短信验证码",
        },        
      },  
      {
        path: '/users',
        component: ListPage,
        meta: {
          title: "管理员",
        },        
      },  
      {
        path: '/discussctripjd',
        component: ListPage,
        meta: {
          title: "景点查询",
        },        
      },  
    ],
  },
  {
    path: '/login',
    component: () => import('@/views/login/login.vue'),
    meta: {
      title: "登录",
    },
  },
  {
    path: '/register',
    component: () => import('@/views/register/register.vue'),
    meta: {
      title: "注册",
    },
  },
  {
    path: '/forgetPassword',
    component: () => import('@/views/forgetPassword.vue'),
    meta: {
      title: '忘记密码',
    },
  },
  {
    path: '/board',
    component: () => import("@/views/decision/DecisionBoard.vue"),
    meta: {
      title: "分析决策",
    },
  },  
]


export default routes
