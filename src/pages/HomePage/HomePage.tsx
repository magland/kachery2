/* eslint-disable @typescript-eslint/no-explicit-any */
import { Hyperlink } from "@fi-sci/misc";
import { FunctionComponent, useEffect, useState } from "react";
import LoginButton from "../../LoginButton";
import useRoute from "../../useRoute";
// import { getGitHubAccessToken } from "./App";

type Props = {
  // none
};

const HomePage: FunctionComponent<Props> = () => {
  const { setRoute } = useRoute();
  const { recentZones } = useRecentZones();
  const a = localStorage.getItem("in-process-of-registering-compute-client");
  return (
    <div style={{ padding: 30 }}>
      <h3>Kachery2: Kachery2 Prototype 3</h3>
      {a && (
        <Hyperlink
          onClick={() => {
            setRoute(JSON.parse(a));
          }}
        >
          CONTINUE REGISTERING COMPUTE CLIENT
        </Hyperlink>
      )}
      <p>
        <a
          href="https://github.com/magland/kachery2"
          target="_blank"
          rel="noopener noreferrer"
        >
          Read more...
        </a>
      </p>
      <div>
        <LoginButton />
      </div>
      <hr />
      <div>
        <div>
          <Hyperlink
            onClick={() => {
              setRoute({ page: "zones" });
            }}
          >
            Zones
          </Hyperlink>
        </div>
      </div>
      {recentZones.length > 0 && (
        <div>
          Recent:{" "}
          {recentZones.map((zoneName) => (
            <span key={zoneName}>
              <Hyperlink
                onClick={() => {
                  setRoute({ page: "zone", zoneName });
                }}
              >
                {zoneName}
              </Hyperlink>
              &nbsp;
            </span>
          ))}
        </div>
      )}
      <hr />
      <div>
        <Hyperlink
          onClick={() => {
            setRoute({ page: "settings" });
          }}
        >
          Settings
        </Hyperlink>
      </div>
    </div>
  );
};

const useRecentZones = () => {
  const [recentZones, setRecentZones] = useState<string[]>([]);
  useEffect(() => {
    const update = () => {
      try {
        const x = localStorage.getItem("recent_zones");
        if (x) {
          const y = JSON.parse(x);
          assertListOfStrings(y);
          setRecentZones(y);
        }
      } catch (err) {
        console.warn(err);
      }
    };
    const timeout = setTimeout(update, 1000);
    return () => {
      clearTimeout(timeout);
    };
  }, []);

  return { recentZones };
};

export const reportRecentZone = (zoneName: string) => {
  let recentZones: string[] = [];
  try {
    const x = localStorage.getItem("recent_zones");
    if (x) {
      recentZones = JSON.parse(x);
      assertListOfStrings(recentZones);
    }
  } catch (err) {
    console.warn(err);
  }
  recentZones = recentZones.filter((name) => name !== zoneName);
  recentZones.unshift(zoneName);
  recentZones = recentZones.slice(0, 10);
  localStorage.setItem("recent_zones", JSON.stringify(recentZones));
};

const assertListOfStrings = (x: any) => {
  if (!Array.isArray(x)) {
    throw new Error("Expected array");
  }
  for (const i in x) {
    if (typeof x[i] !== "string") {
      throw new Error("Expected string");
    }
  }
};

export default HomePage;
