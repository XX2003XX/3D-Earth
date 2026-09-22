html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Earth Space Explorer</title>

<style>
* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #000;
}

body {
    user-select: none;
    touch-action: none;
}

canvas {
    display: block;
    width: 100%;
    height: 100%;
    cursor: grab;
}

canvas:active {
    cursor: grabbing;
}
</style>
</head>

<body>

<script type="module">

import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js";

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(
    55,
    window.innerWidth / window.innerHeight,
    0.01,
    1000
);

camera.position.set(0, 0, 8);

const renderer = new THREE.WebGLRenderer({
    antialias: true,
    powerPreference: "high-performance"
});

renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;

document.body.appendChild(renderer.domElement);

const loader = new THREE.TextureLoader();

const earthGroup = new THREE.Group();
earthGroup.position.set(0, 0, 0);
scene.add(earthGroup);

const blackHoleGroup = new THREE.Group();
blackHoleGroup.position.set(5.2, 0, 0);
blackHoleGroup.visible = false;
scene.add(blackHoleGroup);

const earthTexture = loader.load(
    "https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg"
);

const earthNormal = loader.load(
    "https://threejs.org/examples/textures/planets/earth_normal_2048.jpg"
);

const earthSpecular = loader.load(
    "https://threejs.org/examples/textures/planets/earth_specular_2048.jpg"
);

earthTexture.colorSpace = THREE.SRGBColorSpace;

const earth = new THREE.Mesh(
    new THREE.SphereGeometry(2, 128, 128),
    new THREE.MeshPhongMaterial({
        map: earthTexture,
        normalMap: earthNormal,
        specularMap: earthSpecular,
        specular: new THREE.Color(0x333333),
        shininess: 18
    })
);

earthGroup.add(earth);

const atmosphere = new THREE.Mesh(
    new THREE.SphereGeometry(2.08, 96, 96),
    new THREE.MeshBasicMaterial({
        color: 0x4da6ff,
        transparent: true,
        opacity: 0.13,
        side: THREE.BackSide
    })
);

earthGroup.add(atmosphere);

const ambientLight = new THREE.AmbientLight(
    0xffffff,
    0.35
);

scene.add(ambientLight);

const sunLight = new THREE.DirectionalLight(
    0xffffff,
    2.5
);

sunLight.position.set(5, 3, 5);
scene.add(sunLight);

const starsGeometry = new THREE.BufferGeometry();

const starCount = 8000;

const starPositions = new Float32Array(
    starCount * 3
);

for (let i = 0; i < starCount * 3; i += 3) {

    const radius = 80 + Math.random() * 180;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);

    starPositions[i] =
        radius *
        Math.sin(phi) *
        Math.cos(theta);

    starPositions[i + 1] =
        radius *
        Math.sin(phi) *
        Math.sin(theta);

    starPositions[i + 2] =
        radius *
        Math.cos(phi);
}

starsGeometry.setAttribute(
    "position",
    new THREE.BufferAttribute(
        starPositions,
        3
    )
);

const stars = new THREE.Points(
    starsGeometry,
    new THREE.PointsMaterial({
        color: 0xffffff,
        size: 0.045,
        sizeAttenuation: true
    })
);

scene.add(stars);

const diskGroup = new THREE.Group();

const disk = new THREE.Mesh(
    new THREE.TorusGeometry(
        2.5,
        0.3,
        32,
        256
    ),
    new THREE.MeshBasicMaterial({
        color: 0xff6418,
        transparent: true,
        opacity: 0.9
    })
);

disk.scale.set(
    1.7,
    0.3,
    1
);

diskGroup.add(disk);

const disk2 = new THREE.Mesh(
    new THREE.TorusGeometry(
        3.15,
        0.13,
        24,
        256
    ),
    new THREE.MeshBasicMaterial({
        color: 0xffc15a,
        transparent: true,
        opacity: 0.7
    })
);

disk2.scale.set(
    1.7,
    0.2,
    1
);

diskGroup.add(disk2);

const disk3 = new THREE.Mesh(
    new THREE.TorusGeometry(
        1.85,
        0.12,
        24,
        256
    ),
    new THREE.MeshBasicMaterial({
        color: 0xff2600,
        transparent: true,
        opacity: 0.9
    })
);

disk3.scale.set(
    1.6,
    0.3,
    1
);

diskGroup.add(disk3);

blackHoleGroup.add(diskGroup);

const blackHole = new THREE.Mesh(
    new THREE.SphereGeometry(
        1.45,
        96,
        96
    ),
    new THREE.MeshBasicMaterial({
        color: 0x000000
    })
);

blackHoleGroup.add(blackHole);

const blackHoleGlow = new THREE.Mesh(
    new THREE.SphereGeometry(
        1.72,
        64,
        64
    ),
    new THREE.MeshBasicMaterial({
        color: 0xff5c16,
        transparent: true,
        opacity: 0.08,
        side: THREE.BackSide
    })
);

blackHoleGroup.add(blackHoleGlow);

let mode = "earth";

let earthDistance = 8;
let blackHoleDistance = 7;

let zoomFocus = new THREE.Vector3(
    0,
    0,
    0
);

let portalTarget = new THREE.Vector3(
    5.2,
    0,
    0
);

let transitionProgress = 0;

let dragging = false;

let previousX = 0;
let previousY = 0;

let pointerX = window.innerWidth / 2;
let pointerY = window.innerHeight / 2;

const keys = {
    ArrowUp: false,
    ArrowDown: false,
    ArrowLeft: false,
    ArrowRight: false,
    w: false,
    s: false
};

const raycaster = new THREE.Raycaster();

const mouse = new THREE.Vector2();

function getWorldPointFromMouse() {

    mouse.x =
        (pointerX / window.innerWidth) * 2 - 1;

    mouse.y =
        -(pointerY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(
        mouse,
        camera
    );

    const plane =
        new THREE.Plane(
            new THREE.Vector3(0, 0, 1),
            0
        );

    const point =
        new THREE.Vector3();

    raycaster.ray.intersectPlane(
        plane,
        point
    );

    return point;
}

function moveZoomTowardCursor(delta) {

    const point =
        getWorldPointFromMouse();

    const direction =
        delta < 0 ? 1 : -1;

    const strength =
        THREE.MathUtils.clamp(
            Math.abs(delta) * 0.0012,
            0.01,
            0.18
        );

    const movement =
        point
            .clone()
            .sub(zoomFocus)
            .multiplyScalar(
                strength * direction
            );

    zoomFocus.add(movement);

    const distance =
        zoomFocus.distanceTo(
            new THREE.Vector3(0, 0, 0)
        );

    if (distance > 3.5) {
        zoomFocus.setLength(3.5);
    }

    earthDistance +=
        delta * 0.008;

    earthDistance =
        THREE.MathUtils.clamp(
            earthDistance,
            1.3,
            14
        );
}

function isPointingAtPortal() {

    const portalScreen =
        portalTarget.clone();

    portalScreen.project(camera);

    const x =
        (portalScreen.x + 1) *
        0.5 *
        window.innerWidth;

    const y =
        (-portalScreen.y + 1) *
        0.5 *
        window.innerHeight;

    const distance =
        Math.hypot(
            pointerX - x,
            pointerY - y
        );

    return distance <
        Math.min(
            window.innerWidth,
            window.innerHeight
        ) * 0.25;
}

renderer.domElement.addEventListener(
    "pointerdown",
    event => {

        dragging = true;

        previousX = event.clientX;
        previousY = event.clientY;

        renderer.domElement.setPointerCapture(
            event.pointerId
        );
    }
);

renderer.domElement.addEventListener(
    "pointermove",
    event => {

        pointerX = event.clientX;
        pointerY = event.clientY;

        if (!dragging) return;

        const dx =
            event.clientX - previousX;

        const dy =
            event.clientY - previousY;

        previousX = event.clientX;
        previousY = event.clientY;

        if (mode === "earth") {

            earthGroup.rotation.y +=
                dx * 0.006;

            earthGroup.rotation.x +=
                dy * 0.006;
        }

        if (mode === "blackhole") {

            blackHoleGroup.rotation.y +=
                dx * 0.006;

            blackHoleGroup.rotation.x +=
                dy * 0.006;
        }
    }
);

renderer.domElement.addEventListener(
    "pointerup",
    event => {

        dragging = false;

        renderer.domElement.releasePointerCapture(
            event.pointerId
        );
    }
);

renderer.domElement.addEventListener(
    "pointercancel",
    () => {
        dragging = false;
    }
);

window.addEventListener(
    "keydown",
    event => {

        if (event.key in keys) {
            keys[event.key] = true;
        }

        if (
            event.key === "w" ||
            event.key === "W"
        ) {
            keys.w = true;
        }

        if (
            event.key === "s" ||
            event.key === "S"
        ) {
            keys.s = true;
        }
    }
);

window.addEventListener(
    "keyup",
    event => {

        if (event.key in keys) {
            keys[event.key] = false;
        }

        if (
            event.key === "w" ||
            event.key === "W"
        ) {
            keys.w = false;
        }

        if (
            event.key === "s" ||
            event.key === "S"
        ) {
            keys.s = false;
        }
    }
);

renderer.domElement.addEventListener(
    "wheel",
    event => {

        event.preventDefault();

        if (mode === "earth") {

            moveZoomTowardCursor(
                event.deltaY
            );

            if (
                event.deltaY < 0 &&
                earthDistance < 2.2 &&
                isPointingAtPortal()
            ) {

                mode = "transition";

                transitionProgress = 0;
            }
        }

        else if (mode === "blackhole") {

            blackHoleDistance +=
                event.deltaY * 0.008;

            blackHoleDistance =
                THREE.MathUtils.clamp(
                    blackHoleDistance,
                    2.5,
                    14
                );

            if (
                blackHoleDistance > 10
            ) {

                mode = "return";

                transitionProgress = 1;
            }
        }
    },
    {
        passive: false
    }
);

function keyboardControls() {

    const rotationSpeed = 0.025;
    const zoomSpeed = 0.08;

    if (mode === "earth") {

        if (keys.ArrowLeft)
            earthGroup.rotation.y -= rotationSpeed;

        if (keys.ArrowRight)
            earthGroup.rotation.y += rotationSpeed;

        if (keys.ArrowUp)
            earthGroup.rotation.x -= rotationSpeed;

        if (keys.ArrowDown)
            earthGroup.rotation.x += rotationSpeed;

        if (keys.w)
            earthDistance -= zoomSpeed;

        if (keys.s)
            earthDistance += zoomSpeed;

        earthDistance =
            THREE.MathUtils.clamp(
                earthDistance,
                1.3,
                14
            );

        if (
            keys.w &&
            earthDistance < 2.2 &&
            isPointingAtPortal()
        ) {

            mode = "transition";

            transitionProgress = 0;
        }
    }

    if (mode === "blackhole") {

        if (keys.ArrowLeft)
            blackHoleGroup.rotation.y -= rotationSpeed;

        if (keys.ArrowRight)
            blackHoleGroup.rotation.y += rotationSpeed;

        if (keys.ArrowUp)
            blackHoleGroup.rotation.x -= rotationSpeed;

        if (keys.ArrowDown)
            blackHoleGroup.rotation.x += rotationSpeed;

        if (keys.w)
            blackHoleDistance -= zoomSpeed;

        if (keys.s)
            blackHoleDistance += zoomSpeed;

        blackHoleDistance =
            THREE.MathUtils.clamp(
                blackHoleDistance,
                2.5,
                14
            );

        if (blackHoleDistance > 10) {

            mode = "return";

            transitionProgress = 1;
        }
    }
}

function enterBlackHole() {

    transitionProgress += 0.018;

    const p =
        THREE.MathUtils.smoothstep(
            transitionProgress,
            0,
            1
        );

    camera.position.lerpVectors(
        new THREE.Vector3(
            zoomFocus.x,
            zoomFocus.y,
            2.2
        ),
        new THREE.Vector3(
            portalTarget.x,
            portalTarget.y,
            7
        ),
        p
    );

    camera.lookAt(
        portalTarget
    );

    earthGroup.scale.setScalar(
        1 - p
    );

    if (p > 0.75) {
        earthGroup.visible = false;
        blackHoleGroup.visible = true;
    }

    blackHoleGroup.scale.setScalar(
        Math.max(
            0,
            (p - 0.7) / 0.3
        )
    );

    if (transitionProgress >= 1) {

        mode = "blackhole";

        earthGroup.visible = false;

        blackHoleGroup.visible = true;

        blackHoleGroup.scale.setScalar(1);

        camera.position.set(
            portalTarget.x,
            portalTarget.y,
            blackHoleDistance
        );

        camera.lookAt(
            portalTarget
        );
    }
}

function returnToEarth() {

    transitionProgress -= 0.018;

    const p =
        THREE.MathUtils.smoothstep(
            transitionProgress,
            0,
            1
        );

    camera.position.lerpVectors(
        new THREE.Vector3(
            portalTarget.x,
            portalTarget.y,
            blackHoleDistance
        ),
        new THREE.Vector3(
            0,
            0,
            earthDistance
        ),
        1 - p
    );

    camera.lookAt(
        new THREE.Vector3(
            0,
            0,
            0
        )
    );

    blackHoleGroup.scale.setScalar(
        p
    );

    if (p < 0.3) {
        blackHoleGroup.visible = false;
        earthGroup.visible = true;
    }

    earthGroup.scale.setScalar(
        Math.max(
            0,
            (0.3 - p) / 0.3
        )
    );

    if (transitionProgress <= 0) {

        mode = "earth";

        blackHoleGroup.visible = false;

        earthGroup.visible = true;

        earthGroup.scale.setScalar(1);

        earthGroup.position.set(
            0,
            0,
            0
        );

        zoomFocus.set(
            0,
            0,
            0
        );

        camera.position.set(
            0,
            0,
            earthDistance
        );

        camera.lookAt(
            0,
            0,
            0
        );
    }
}

function animate() {

    requestAnimationFrame(animate);

    keyboardControls();

    if (mode === "earth") {

        earthGroup.visible = true;

        blackHoleGroup.visible = false;

        camera.position.x =
            zoomFocus.x;

        camera.position.y =
            zoomFocus.y;

        camera.position.z =
            earthDistance;

        camera.lookAt(
            zoomFocus
        );
    }

    if (mode === "blackhole") {

        earthGroup.visible = false;

        blackHoleGroup.visible = true;

        camera.position.set(
            portalTarget.x,
            portalTarget.y,
            blackHoleDistance
        );

        camera.lookAt(
            portalTarget
        );

        diskGroup.rotation.z +=
            0.012;
    }

    if (mode === "transition") {
        enterBlackHole();
    }

    if (mode === "return") {
        returnToEarth();
    }

    stars.rotation.y +=
        0.00012;

    renderer.render(
        scene,
        camera
    );
}

window.addEventListener(
    "resize",
    () => {

        camera.aspect =
            window.innerWidth /
            window.innerHeight;

        camera.updateProjectionMatrix();

        renderer.setSize(
            window.innerWidth,
            window.innerHeight
        );
    }
);

animate();

</script>

</body>
</html>
"""

with open("earth_space_explorer.html", "w", encoding="utf-8") as f:
    f.write(html_content)