// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Contains current user email and first/last name
        user_email: user_email,
        username: username,

        // Stores all posts
        posts: [],

        // Used to toggle new post display
        showNewPost: false,

        // Text when user creates new post
        post_text: '',

    };

    app.addNewPost = () => {
        // We send the data to the server, from which we get the id
        axios.post(add_post_url, {
            post_text: app.data.post_text
        }).then(function (response) {
            // Add the post from the textarea input
            let length = app.data.posts.push({
                id: response.data.id,
                name: app.data.username,
                post_text: app.data.post_text,
                user_email: app.data.user_email,
                _idx: app.data.posts.length,
            });

            // Using Vue.set() so rating property is reactive
            Vue.set(app.data.posts[length - 1], 'rating', 0);
            
            

            app.toggleNewPost();
        });
    };

    app.deletePost = (id, _idx) => {
        axios.post(delete_post_url, {
            post_id: id

        }).then(function () {
            app.data.posts.splice(_idx, 1);
            app.reindex(app.data.posts);

        }).catch(function (error) {
            console.log(error);
        });
    };

    app.completeProperties = (posts) => {
        posts.map((post) => {
            // Predefined property because vue can only observe attributes of posts that are defined
            // when posts is defined as a data property of vue
            post.rating = 0;
        })
    };

    // Add here the various functions you need.
    app.toggleNewPost = () => {
        app.data.showNewPost = !app.data.showNewPost;
    };

    app.setRating = (_idx, type) => {
        let post = app.data.posts[_idx];
        post.rating = type;
        axios.post(set_rating_url,{
            post_rating: post.rating,
            post_id: post.id
        });
    };


    app.hoverOver = (_idx) => {
        //app.data.posts[id].toggleThumb = 'up';
    };

    app.hoverOff = (_idx) => {

    };

    // Use this function to reindex the posts, when you get them, and when
    // you add / delete one of them.
    app.reindex = (a) => {
        let idx = 0;

        for (p of a) {
            p._idx = idx++;
            // Add here whatever other attributes should be part of a post.
        }
        return a;
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        reindex: app.reindex,
        toggleNewPost: app.toggleNewPost,
        addNewPost: app.addNewPost,
        deletePost: app.deletePost,
        completeProperties: app.completeProperties,
        hoverOver: app.hoverOver,
        hoverOff: app.hoverOff,
        setRating: app.setRating
        
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
    });

    // And this initializes it.
    app.init = () => {
        // Retrieving all posts from the database
        axios.get(get_posts_url).then((result) => {
            
            let posts = result.data.posts;
            // Reindexing the posts 
            app.reindex(posts);
            // Adding additional properties to posts
            app.completeProperties(posts);
            // Setting posts as a property in app.data after so that 
            // vue can track all properties 
            app.data.posts = posts;
        }).then(() => {
            // Get the ratings for each post
            // Based on the user
            for (let post of app.data.posts) {
                console.log(post.id);
                axios.get(get_ratings_url, {post_id: post.id})
                    .then((result) => {
                        post.rating = result.data.rating;

                })
            }
        })
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);