// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        posts: [], // See initialization.
    };

    app.index = (a) => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;
        for (let p of a) {
            // For webpage displaying
            p._idx = i++;
            p.editable = (user_email == p.email) ? true : false; 
            p.edit = false;
            p.is_pending = false;
            p.error = false;
            p.original_content = p.content; // Content before an edit.
            p.server_content = p.content; // Content on the server.
        }
        return a;
    };

    app.reindex = () => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;
        // Indexing all posts for ordering on the webpage
        // Used after get_posts()
        for (let p of app.vue.posts) {
            // Doesn't use Vue.set() since don't need _idx to be reactive
            // Won't be reactive since app.vue.posts is already initialized
            p._idx = i++;
        }
    };

    // Handler for button that starts the edit.
    // Make sure that no OTHER post is being edited.
    // If so, do nothing. Otherwise, proceed as below.
    app.do_edit = (post_idx) => {

        // Post to edit
        let p = app.vue.posts[post_idx];

        if (p.editable && app.only_edit()) {

            // Set edit property to true to display textarea
            p.edit = true;
            p.is_pending = false;    
        }     
    };

    // Helper function for do_edit()
    app.only_edit = () => {

        for (post of app.data.posts) {
            if(post.edit == true) {
                return false;
            }
        }

        return true;
    }

    // Handler for button that cancels the edit.
    app.do_cancel = (post_idx) => {

        let p = app.vue.posts[post_idx];
        if (p.id === null) {
            // If the post has not been saved yet, we delete it.
            app.vue.posts.splice(post_idx, 1);
            // Reindex posts _idx of posts after cancelled post is removed
            app.reindex();
        } else {
            // We go back to before the edit.

            // Set edit property to false to hide textarea
            p.edit = false;
            p.is_pending = false;

            // Set content propety back to content before the edit
            p.content = p.original_content;
        }
    }

    // Handler for "Save edit" button.
    app.do_save = (post_idx) => {

        // Post to save
        let p = app.vue.posts[post_idx];

        // Check if content of post was changed
        if (p.content !== p.server_content) {
            p.is_pending = true;
            
            /*
                params:
                    - p.content  (text in post)
                    - p.id       (database id of post)
                    - p.is_reply (bool for post vs. reply)
                    
            */

            // Call to server to save post in the database
            axios.post(posts_url, {
                content: p.content,
                id: p.id,
                is_reply: p.is_reply,
            }).then((result) => {
                console.log("Received:", result.data);
                
                // Set edit property to false to hide textarea
                p.edit = false;

                // Set id property to id returned from server (for new posts)
                p.id = result.data.id;

                // Update original_content and server_content with content returned from server
                p.original_content = p.server_content = result.data.content;

            }).catch(() => {
                p.is_pending = false;
                console.log("Caught error");
                // We stay in edit mode.
            });
        } else {
            // No need to save.
            p.edit = false;

            // Post content didn't change so set original content as current content
            p.original_content = p.content;
        }
    }

    app.add_post = () => {

        // You need to initialize it properly, completing below, and ...
        // Mostly null since values will be initialized when saved 
        let new_post = {

            // General: Distinguish between posts
            // Starts as null since post hasn't been added to database
            id: null,

            // Edit: Toggle when to display edit post features
            edit: true,

            // Edit: Determine who can edit the post (owner)
            editable: true,

            // General: Save current post content
            // Starts as empty string
            content: "",

            // Add/Edit: Content stored on server
            // Starts as null since post hasn't been sent to server
            server_content: null,

            // Add/Edit: Track content between edits
            // Starts as empty string
            original_content: "",

            // General: Identify post owner
            author: author_name,
            email: user_email,

            // Reply: id of main post
            // Set to null since add_post() only creates posts
            is_reply: null,
        };

        // Insert post at the top of the post list.
        app.data.posts.push(new_post);
        app.reindex();
    };


    // Initializes replies
    app.reply = (post_idx) => {

        // Post that new reply is replying to
        let p = app.vue.posts[post_idx];

        // Check if post exists
        if (p.id !== null) {
            
            // Initializing new reply
            let new_reply = {
                id: null,
                edit: true,
                editable: true,
                content: "",
                server_content: null,
                original_content: "",
                author: author_name,
                email: user_email,
                is_reply: p.id,
            };

            // Insert reply immediately before post replied to in posts
            app.data.posts.splice(p._idx, 0, new_reply);

            // Reindex _idx since new element is added into list
            app.reindex();
        }
    };

    app.do_delete = (post_idx) => {

        // Post to delete
        let p = app.vue.posts[post_idx];

        // If the post has never been added to the server,
        // simply deletes it from the list of posts.
        if (p.id === null) {
            app.data.posts.splice(post_idx, 1);
            
        } else {   
            // Call to server deleting post from database
            axios.post(delete_url,{id: p.id}).then(() => {

                // Remove post from posts list after database removal
                app.data.posts.splice(post_idx, 1);
                
            })
        }

        //Reindex the posts since element was removed from list
        app.reindex();
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    // Only methods used in index.html
    app.methods = {
        do_edit: app.do_edit,
        do_cancel: app.do_cancel,
        do_save: app.do_save,
        add_post: app.add_post,
        reply: app.reply,
        do_delete: app.do_delete,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        // Connects Vue object to specified HTML tag in index.html
        el: "#vue-target",

        // Set data property as app.data
        data: app.data,

        // Set methods propety as app.methods
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Load posts from the server
        axios.get(posts_url).then((result) => {
            
            let posts = result.data.posts;

            app.vue.posts = app.index(posts);
        })   
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
