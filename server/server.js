const websocket = require("ws");
const wss = new websocket.WebSocketServer({ port: 8080 });
let connected_players = [];
let playersData = [];
const readline = require("node:readline/promises");
const { stdin: input, stdout: output } = require("node:process");

console.log("WebSocket for Wishdenring has started at port: 8080 ");

wss.on("connection", function connection(ws) {
  ws.on("error", console.error);
  //console.log(`New user has connected`);
  ws.on("message", function message(data) {
    const received = JSON.parse(data);

    if (received.identifier) {
      //  --- On connect only ---
      if (!connected_players.includes(received.identifier)) {
        connected_players.push(received.identifier);
      }
      //console.log("All users connected:", connected_players);
      ws.send("connected");
    } else {
      //  --- On data update ---
      //console.log("Player data", JSON.stringify(received));
      const uuid = received[Object.keys(received)[0]].data.identifier;
      let hasfound = false;
      playersData.forEach((client) => {
        if (Object.values(client)[0].data.identifier === uuid) hasfound = true;
      });
      if (!hasfound) {
        //when 1st time connecting
        console.log("New player is connecting !");
        let newArray = [...playersData, received];
        playersData = newArray;
        ws.send(
          JSON.stringify({
            connected_users: connected_players,
            playersData: playersData,
          })
        );
      } else {
        //when need to update data
        //console.log("Has found user in array", playersData);
        const newPlayers = playersData.filter(
          (client) => Object.values(client)[0].data.identifier !== uuid
        );
        let newArray = [...newPlayers, received];
        playersData = newArray;
        ws.send(
          JSON.stringify({
            connected_users: connected_players,
            playersData: playersData,
          })
        );
      }
    }
  });
});

/* const rl = readline.createInterface({ input, output });

rl.question("What do you think of Node.js? ", (answer) => {
  // TODO: Log the answer in a database
  console.log(`Thank you for your valuable feedback: ${answer}`);

  rl.close();
}); */
