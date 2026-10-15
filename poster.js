const movieKey = fetch("t0-free-rpdb").then(
    (response)=>{
        return response.json();
    }
).then(
    (data)=>{
        console.log(data);
    }
)