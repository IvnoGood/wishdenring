const test = [
  {
    "08bc90e8-95d5-4b17-819c-55f5990993f9": {
      data: { identifier: "08bc90e8-95d5-4b17-819c-55f5990993f9" },
      player: {
        location: "Vec3(10.397321, 0.5600037, -0.69232445)",
        rotation: "Vec3(17.249994, -214.04515, 0)",
      },
    },
  },
  {
    "29e4dcb7-7002-4e07-ace9-faa812207d63": {
      data: { identifier: "29e4dcb7-7002-4e07-ace9-faa812207d63" },
      player: { location: "Vec3(0, 1.0005777, 0)", rotation: "Vec3(0, 0, 0)" },
    },
  },
];

test.forEach((client) => {
  console.log(client);
});
