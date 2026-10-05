import React, { useEffect, useRef } from "react";

interface CinematicVideoProps {
  src: string;
  className?: string;
  poster?: string;
}

export const CinematicVideo: React.FC<CinematicVideoProps> = ({
  src,
  className = "",
  poster,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    // Strictly enforce muted properties at DOM level (required by Chrome/WebKit autoplay policies)
    video.muted = true;
    video.defaultMuted = true;
    video.playsInline = true;

    const attemptPlay = () => {
      if (!video) return;
      const playPromise = video.play();
      if (playPromise !== undefined) {
        playPromise.catch((err) => {
          // Autoplay was blocked or deferred by the browser
          console.warn("Autoplay deferred by browser policy, queuing on user gesture:", err);
          
          const onUserGesture = () => {
            if (videoRef.current) {
              videoRef.current.play().catch(() => {});
            }
            cleanupListeners();
          };

          const cleanupListeners = () => {
            window.removeEventListener("click", onUserGesture);
            window.removeEventListener("touchstart", onUserGesture);
            window.removeEventListener("scroll", onUserGesture);
            window.removeEventListener("keydown", onUserGesture);
          };

          window.addEventListener("click", onUserGesture, { once: true, passive: true });
          window.addEventListener("touchstart", onUserGesture, { once: true, passive: true });
          window.addEventListener("scroll", onUserGesture, { once: true, passive: true });
          window.addEventListener("keydown", onUserGesture, { once: true, passive: true });
        });
      }
    };

    if (video.readyState >= 2) {
      attemptPlay();
    } else {
      video.addEventListener("canplay", attemptPlay, { once: true });
      video.addEventListener("loadeddata", attemptPlay, { once: true });
    }

    // Auto-resume if video paused unexpectedly while tab is active
    const handlePause = () => {
      if (!document.hidden && video.paused) {
        video.play().catch(() => {});
      }
    };
    video.addEventListener("pause", handlePause);

    return () => {
      video.removeEventListener("pause", handlePause);
    };
  }, [src]);

  return (
    <video
      ref={videoRef}
      src={src}
      autoPlay
      loop
      muted
      playsInline
      preload="auto"
      poster={poster}
      className={className}
    />
  );
};
